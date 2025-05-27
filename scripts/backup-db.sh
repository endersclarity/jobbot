#!/bin/bash

# JobBot Production Database Backup Script
# Automated daily backup with retention and monitoring

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
ARCHIVE_DIR="/backups/archive"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="jobbot_backup_${TIMESTAMP}.sql.gz"
LOG_FILE="/backups/backup.log"

# Database connection settings from environment
PGHOST=${PGHOST:-postgres}
PGPORT=${PGPORT:-5432}
PGDATABASE=${PGDATABASE:-jobbot_prod}
PGUSER=${PGUSER:-jobbot_user}

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Cleanup old backups
cleanup_old_backups() {
    log "Starting cleanup of old backups (retention: ${RETENTION_DAYS} days)"
    
    find "$BACKUP_DIR" -name "jobbot_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
    find "$ARCHIVE_DIR" -name "*.backup" -type f -mtime +${RETENTION_DAYS} -delete
    
    log "Cleanup completed"
}

# Health check before backup
health_check() {
    log "Performing database health check"
    
    # Check database connectivity
    if ! pg_isready -h "$PGHOST" -p "$PGPORT" -d "$PGDATABASE" -U "$PGUSER"; then
        error_exit "Database is not accessible"
    fi
    
    # Check disk space (require at least 1GB free)
    AVAILABLE_SPACE=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then  # 1GB in KB
        error_exit "Insufficient disk space for backup (less than 1GB available)"
    fi
    
    log "Health check passed"
}

# Create full database backup
create_backup() {
    log "Starting database backup to ${BACKUP_FILE}"
    
    # Full database dump with compression
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
        --file="${BACKUP_DIR}/${BACKUP_FILE%.gz}" 2>>"$LOG_FILE"; then
        
        # Compress the backup
        gzip "${BACKUP_DIR}/${BACKUP_FILE%.gz}"
        log "Backup completed successfully: ${BACKUP_FILE}"
    else
        error_exit "Backup failed - check log for details"
    fi
}

# Create point-in-time recovery archive
create_archive() {
    local archive_file="jobbot_archive_${TIMESTAMP}.backup"
    
    log "Creating point-in-time recovery archive: ${archive_file}"
    
    if pg_dump \
        --host="$PGHOST" \
        --port="$PGPORT" \
        --username="$PGUSER" \
        --dbname="$PGDATABASE" \
        --no-password \
        --format=tar \
        --compress=9 \
        --file="${ARCHIVE_DIR}/${archive_file}" 2>>"$LOG_FILE"; then
        
        log "Archive completed successfully: ${archive_file}"
    else
        log "WARNING: Archive creation failed - continuing with backup"
    fi
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity"
    
    # Check if backup file exists and is not empty
    if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ] || [ ! -s "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
        error_exit "Backup file is missing or empty"
    fi
    
    # Test backup file integrity
    if ! gzip -t "${BACKUP_DIR}/${BACKUP_FILE}"; then
        error_exit "Backup file is corrupted"
    fi
    
    log "Backup integrity verified"
}

# Generate backup report
generate_report() {
    local backup_size=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    local total_backups=$(find "$BACKUP_DIR" -name "jobbot_backup_*.sql.gz" | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    
    log "=== BACKUP REPORT ==="
    log "Backup file: ${BACKUP_FILE}"
    log "Backup size: ${backup_size}"
    log "Total backups: ${total_backups}"
    log "Total backup storage: ${total_size}"
    log "Retention policy: ${RETENTION_DAYS} days"
    log "===================="
}

# Send notification (placeholder for future implementation)
send_notification() {
    local status=$1
    local message=$2
    
    # Future: Send notification via email, Slack, etc.
    log "NOTIFICATION: ${status} - ${message}"
}

# Main backup process
main() {
    log "========================================="
    log "Starting JobBot database backup process"
    log "========================================="
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR" "$ARCHIVE_DIR"
    
    # Ensure log file exists
    touch "$LOG_FILE"
    
    # Execute backup process
    health_check
    cleanup_old_backups
    create_backup
    create_archive
    verify_backup
    generate_report
    
    log "Backup process completed successfully"
    send_notification "SUCCESS" "Database backup completed: ${BACKUP_FILE}"
}

# Error trap
trap 'error_exit "Backup process failed at line $LINENO"' ERR

# Execute main process
main "$@"