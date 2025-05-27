#!/bin/bash

# JobBot Production Database Restore Script
# Automated database restoration with validation and rollback capabilities

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/backups"
RESTORE_LOG="/backups/restore.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database connection settings
PGHOST=${PGHOST:-postgres}
PGPORT=${PGPORT:-5432}
PGDATABASE=${PGDATABASE:-jobbot_prod}
PGUSER=${PGUSER:-jobbot_user}

# Restore settings
BACKUP_FILE=""
DRY_RUN=false
FORCE_RESTORE=false
CREATE_BACKUP_BEFORE_RESTORE=true

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$RESTORE_LOG"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$RESTORE_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$RESTORE_LOG"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$RESTORE_LOG"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS] BACKUP_FILE"
    echo ""
    echo "Options:"
    echo "  --dry-run                 Show what would be restored without making changes"
    echo "  --force                   Skip confirmation prompts"
    echo "  --no-backup              Skip creating backup before restore"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 jobbot_backup_20241201_120000.sql.gz"
    echo "  $0 --dry-run jobbot_backup_20241201_120000.sql.gz"
    echo "  $0 --force --no-backup latest_backup.sql.gz"
    echo ""
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE_RESTORE=true
                shift
                ;;
            --no-backup)
                CREATE_BACKUP_BEFORE_RESTORE=false
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                if [[ -z "$BACKUP_FILE" ]]; then
                    BACKUP_FILE="$1"
                else
                    error "Multiple backup files specified"
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$BACKUP_FILE" ]]; then
        error "Backup file is required"
    fi
}

# Validate backup file
validate_backup_file() {
    log "Validating backup file: $BACKUP_FILE"
    
    # Check if file exists
    if [[ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]]; then
        error "Backup file not found: ${BACKUP_DIR}/${BACKUP_FILE}"
    fi
    
    # Check file integrity
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        if ! gzip -t "${BACKUP_DIR}/${BACKUP_FILE}"; then
            error "Backup file is corrupted: $BACKUP_FILE"
        fi
    fi
    
    # Get file info
    local file_size=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    local file_date=$(stat -c %y "${BACKUP_DIR}/${BACKUP_FILE}")
    
    log "Backup file validation successful"
    log "File size: $file_size"
    log "File date: $file_date"
}

# Health check before restore
pre_restore_health_check() {
    log "Performing pre-restore health check"
    
    # Check database connectivity
    if ! pg_isready -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -U "$PGUSER"; then
        error "Database is not accessible"
    fi
    
    # Check disk space (require at least 2GB free)
    local available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 2097152 ]; then  # 2GB in KB
        error "Insufficient disk space for restore operation (less than 2GB available)"
    fi
    
    # Check for active connections
    local active_connections=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname = '$PGDATABASE' AND state = 'active';" 2>/dev/null || echo "0")
    
    if [[ "$active_connections" -gt 5 ]]; then
        warn "High number of active connections detected: $active_connections"
        if [[ "$FORCE_RESTORE" != "true" ]]; then
            read -p "Continue with restore? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                error "Restore cancelled by user"
            fi
        fi
    fi
    
    success "Pre-restore health check passed"
}

# Create backup before restore
create_pre_restore_backup() {
    if [[ "$CREATE_BACKUP_BEFORE_RESTORE" == "true" ]]; then
        log "Creating backup before restore operation"
        
        local pre_restore_backup="pre_restore_backup_${TIMESTAMP}.sql.gz"
        
        if pg_dump \
            --host="$PGHOST" \
            --port="$PGPORT" \
            --username="$PGUSER" \
            --dbname="$PGDATABASE" \
            --no-password \
            --verbose \
            --format=custom \
            --compress=9 \
            --no-privileges \
            --no-owner \
            --file="${BACKUP_DIR}/${pre_restore_backup%.gz}" 2>>"$RESTORE_LOG"; then
            
            gzip "${BACKUP_DIR}/${pre_restore_backup%.gz}"
            log "Pre-restore backup created: $pre_restore_backup"
        else
            error "Failed to create pre-restore backup"
        fi
    else
        log "Skipping pre-restore backup (--no-backup specified)"
    fi
}

# Terminate active connections
terminate_connections() {
    log "Terminating active connections to database"
    
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '$PGDATABASE'
        AND pid <> pg_backend_pid()
        AND state = 'active';
    " 2>>"$RESTORE_LOG" || warn "Could not terminate all connections"
}

# Perform database restore
perform_restore() {
    log "Starting database restore from: $BACKUP_FILE"
    
    local backup_path="${BACKUP_DIR}/${BACKUP_FILE}"
    local restore_cmd=""
    
    # Determine restore command based on file format
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        # Compressed backup
        restore_cmd="gunzip -c '$backup_path' | pg_restore"
    else
        # Uncompressed backup
        restore_cmd="pg_restore '$backup_path'"
    fi
    
    # Add connection parameters
    restore_cmd="$restore_cmd --host=$PGHOST --port=$PGPORT --username=$PGUSER --dbname=$PGDATABASE"
    restore_cmd="$restore_cmd --verbose --clean --if-exists --no-owner --no-privileges"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would execute restore command:"
        log "$restore_cmd"
        return 0
    fi
    
    # Execute restore
    if eval "$restore_cmd" 2>>"$RESTORE_LOG"; then
        success "Database restore completed successfully"
    else
        error "Database restore failed - check log for details"
    fi
}

# Verify restore integrity
verify_restore() {
    log "Verifying restore integrity"
    
    # Check database connectivity
    if ! pg_isready -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -U "$PGUSER"; then
        error "Database is not accessible after restore"
    fi
    
    # Check table count
    local table_count=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")
    
    if [[ "$table_count" -lt 5 ]]; then
        warn "Low table count detected: $table_count (expected at least 5)"
    else
        log "Table count verification passed: $table_count tables"
    fi
    
    # Check for critical tables
    local critical_tables=("jobs" "applications" "companies" "opportunities")
    for table in "${critical_tables[@]}"; do
        local exists=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '$table');" 2>/dev/null || echo "f")
        
        if [[ "$exists" == "t" ]]; then
            log "Critical table verified: $table"
        else
            warn "Critical table missing: $table"
        fi
    done
    
    success "Restore integrity verification completed"
}

# Generate restore report
generate_restore_report() {
    local restore_size=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    local total_tables=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "Unknown")
    
    log "=== RESTORE REPORT ==="
    log "Backup file: ${BACKUP_FILE}"
    log "Backup size: ${restore_size}"
    log "Total tables restored: ${total_tables}"
    log "Restore timestamp: ${TIMESTAMP}"
    
    if [[ "$CREATE_BACKUP_BEFORE_RESTORE" == "true" ]]; then
        log "Pre-restore backup: pre_restore_backup_${TIMESTAMP}.sql.gz"
    fi
    
    log "======================="
}

# Confirmation prompt
confirm_restore() {
    if [[ "$FORCE_RESTORE" == "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}WARNING: This will replace the current database with the backup data!${NC}"
    echo "Database: $PGDATABASE"
    echo "Backup file: $BACKUP_FILE"
    echo ""
    
    if [[ "$CREATE_BACKUP_BEFORE_RESTORE" == "true" ]]; then
        echo "A backup of the current database will be created before restore."
    else
        echo "NO backup will be created before restore."
    fi
    
    echo ""
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Restore cancelled by user"
    fi
}

# Main restore process
main() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "   JobBot Database Restore Process"
    echo "========================================"
    echo -e "${NC}"
    
    parse_args "$@"
    
    # Create restore log
    mkdir -p "$BACKUP_DIR"
    touch "$RESTORE_LOG"
    
    log "Starting restore process for: $BACKUP_FILE"
    
    validate_backup_file
    pre_restore_health_check
    confirm_restore
    
    if [[ "$DRY_RUN" != "true" ]]; then
        create_pre_restore_backup
        terminate_connections
    fi
    
    perform_restore
    
    if [[ "$DRY_RUN" != "true" ]]; then
        verify_restore
        generate_restore_report
        log "Restore process completed successfully"
    else
        log "DRY RUN completed - no changes made"
    fi
}

# Error trap
trap 'error "Restore process failed at line $LINENO"' ERR

# Execute main process
main "$@"