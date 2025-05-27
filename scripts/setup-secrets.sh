#!/bin/bash

# JobBot Production Secrets Management Setup Script
# Generates secure secrets and configures production environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env.production"
ENV_EXAMPLE=".env.production.example"
SECRETS_DIR="./secrets"
BACKUP_DIR="./backups/env-backup"

# Logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    local deps=("openssl" "docker" "docker-compose")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Required dependency '$dep' is not installed"
        fi
    done
    
    success "All dependencies are available"
}

# Generate secure password
generate_password() {
    local length=${1:-32}
    openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-${length}
}

# Generate hex key
generate_hex_key() {
    local length=${1:-32}
    openssl rand -hex "$length"
}

# Create secrets directory
setup_secrets_directory() {
    log "Setting up secrets directory..."
    
    mkdir -p "$SECRETS_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Set secure permissions
    chmod 700 "$SECRETS_DIR"
    chmod 700 "$BACKUP_DIR"
    
    success "Secrets directory created with secure permissions"
}

# Backup existing environment file
backup_existing_env() {
    if [ -f "$ENV_FILE" ]; then
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="${BACKUP_DIR}/env_backup_${timestamp}"
        
        log "Backing up existing environment file..."
        cp "$ENV_FILE" "$backup_file"
        success "Environment file backed up to: $backup_file"
    fi
}

# Generate all required secrets
generate_secrets() {
    log "Generating secure secrets..."
    
    # Application secrets
    SECRET_KEY=$(generate_hex_key 32)
    
    # Database passwords
    POSTGRES_PASSWORD=$(generate_password 24)
    APP_USER_PASSWORD=$(generate_password 24)
    READONLY_PASSWORD=$(generate_password 24)
    BACKUP_PASSWORD=$(generate_password 24)
    
    # Redis password
    REDIS_PASSWORD=$(generate_password 16)
    
    # Monitoring passwords
    GRAFANA_ADMIN_PASSWORD=$(generate_password 16)
    
    # Email passwords (placeholders - to be filled manually)
    GMAIL_APP_PASSWORD="your-gmail-app-password-here"
    MONITORING_EMAIL_PASSWORD="your-monitoring-email-password"
    
    success "All secrets generated successfully"
}

# Create production environment file
create_production_env() {
    log "Creating production environment file..."
    
    if [ ! -f "$ENV_EXAMPLE" ]; then
        error "Environment example file '$ENV_EXAMPLE' not found"
    fi
    
    # Copy example file
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    
    # Replace placeholder values with generated secrets
    sed -i "s/your-super-secret-key-here-generate-with-openssl-rand-hex-32/$SECRET_KEY/g" "$ENV_FILE"
    sed -i "s/your-secure-postgres-password-here/$POSTGRES_PASSWORD/g" "$ENV_FILE"
    sed -i "s/your-app-user-password/$APP_USER_PASSWORD/g" "$ENV_FILE"
    sed -i "s/your-redis-password-here/$REDIS_PASSWORD/g" "$ENV_FILE"
    sed -i "s/your-secure-grafana-password-here/$GRAFANA_ADMIN_PASSWORD/g" "$ENV_FILE"
    
    # Set secure permissions
    chmod 600 "$ENV_FILE"
    
    success "Production environment file created: $ENV_FILE"
}

# Save secrets to secure file
save_secrets_file() {
    log "Saving secrets to secure file..."
    
    local secrets_file="${SECRETS_DIR}/production-secrets.txt"
    
    cat > "$secrets_file" << EOF
# JobBot Production Secrets
# Generated: $(date)
# KEEP THIS FILE SECURE AND PRIVATE

========================================
Application Secrets
========================================
SECRET_KEY=$SECRET_KEY

========================================
Database Passwords
========================================
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
APP_USER_PASSWORD=$APP_USER_PASSWORD
READONLY_PASSWORD=$READONLY_PASSWORD
BACKUP_PASSWORD=$BACKUP_PASSWORD

========================================
Redis Password
========================================
REDIS_PASSWORD=$REDIS_PASSWORD

========================================
Monitoring Passwords
========================================
GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD

========================================
Manual Configuration Required
========================================
The following secrets must be configured manually:

1. API Keys:
   - OPENAI_API_KEY=your-openai-api-key-here
   - GEMINI_API_KEY=your-gemini-api-key-here
   - GITHUB_TOKEN=your-github-token-here
   - EXA_API_KEY=your-exa-api-key-here

2. Email Configuration:
   - GMAIL_APP_PASSWORD=your-gmail-app-password-here
   - MONITORING_EMAIL_PASSWORD=your-monitoring-email-password

3. SSL Certificates:
   - Generate or obtain SSL certificates
   - Place in /etc/ssl/certs/ and /etc/ssl/private/
   - Update SSL_CERT_PATH and SSL_KEY_PATH in $ENV_FILE

4. Domain Configuration:
   - Update GRAFANA_DOMAIN with your actual domain
   - Update CORS_ORIGINS with your domains

========================================
Security Checklist
========================================
□ Change default passwords in database initialization script
□ Configure SSL certificates
□ Update API keys and tokens
□ Set up domain names and DNS
□ Configure firewall rules
□ Set up backup storage (S3/etc)
□ Test all connections and services
□ Enable monitoring and alerting
□ Perform security audit
□ Document recovery procedures

EOF

    chmod 600 "$secrets_file"
    success "Secrets saved to: $secrets_file"
}

# Generate SSL certificate (self-signed for development)
generate_ssl_certificate() {
    log "Generating self-signed SSL certificate for development..."
    
    local ssl_dir="./ssl"
    mkdir -p "$ssl_dir"
    
    # Generate private key
    openssl genrsa -out "${ssl_dir}/jobbot.key" 2048
    
    # Generate certificate signing request
    openssl req -new -key "${ssl_dir}/jobbot.key" -out "${ssl_dir}/jobbot.csr" -subj "/C=US/ST=CA/L=City/O=Organization/OU=OrgUnit/CN=localhost"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "${ssl_dir}/jobbot.csr" -signkey "${ssl_dir}/jobbot.key" -out "${ssl_dir}/jobbot.crt"
    
    # Set secure permissions
    chmod 600 "${ssl_dir}/jobbot.key"
    chmod 644 "${ssl_dir}/jobbot.crt"
    
    # Clean up CSR
    rm "${ssl_dir}/jobbot.csr"
    
    warn "Self-signed certificate generated for development only"
    warn "For production, use proper SSL certificates from Let's Encrypt or commercial CA"
    
    success "SSL certificate generated: ${ssl_dir}/jobbot.crt"
}

# Validate environment file
validate_environment() {
    log "Validating environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file '$ENV_FILE' not found"
    fi
    
    # Check for placeholder values
    local placeholders=(
        "your-openai-api-key-here"
        "your-gmail-app-password-here"
        "your-domain.com"
    )
    
    for placeholder in "${placeholders[@]}"; do
        if grep -q "$placeholder" "$ENV_FILE"; then
            warn "Placeholder value '$placeholder' found in $ENV_FILE - manual configuration required"
        fi
    done
    
    success "Environment file validation completed"
}

# Display next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   SECRETS SETUP COMPLETED${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Review and update API keys in: $ENV_FILE"
    echo "2. Configure email passwords for notifications"
    echo "3. Set up proper SSL certificates for production"
    echo "4. Update domain names and CORS origins"
    echo "5. Test the configuration:"
    echo -e "   ${BLUE}docker-compose -f docker-compose.prod.yml config${NC}"
    echo ""
    echo "6. Deploy to production:"
    echo -e "   ${BLUE}docker-compose -f docker-compose.prod.yml up -d${NC}"
    echo ""
    echo -e "${RED}IMPORTANT SECURITY REMINDERS:${NC}"
    echo "• Never commit .env.production to version control"
    echo "• Keep secrets file secure and backed up"
    echo "• Rotate secrets regularly"
    echo "• Monitor access logs"
    echo "• Use proper SSL certificates in production"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "   JobBot Production Secrets Setup"
    echo "========================================"
    echo -e "${NC}"
    
    check_dependencies
    setup_secrets_directory
    backup_existing_env
    generate_secrets
    create_production_env
    save_secrets_file
    generate_ssl_certificate
    validate_environment
    show_next_steps
}

# Run main function
main "$@"