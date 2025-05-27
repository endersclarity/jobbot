#!/bin/bash

# JobBot SSL Certificate Setup Script
# Supports both Let's Encrypt (production) and self-signed (development) certificates

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSL_DIR="./ssl"
CERT_DIR="/etc/ssl/certs"
KEY_DIR="/etc/ssl/private"
DOMAIN="localhost"  # Default domain, override with --domain
EMAIL=""            # Required for Let's Encrypt
MODE="development"  # development or production

# Logging functions
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

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --mode MODE           Certificate mode: development or production (default: development)"
    echo "  --domain DOMAIN       Domain name for the certificate (default: localhost)"
    echo "  --email EMAIL         Email for Let's Encrypt registration (required for production)"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --mode development                    # Generate self-signed certificate"
    echo "  $0 --mode production --domain example.com --email admin@example.com"
    echo ""
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode)
                MODE="$2"
                shift 2
                ;;
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --email)
                EMAIL="$2"
                shift 2
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Validate mode
    if [[ "$MODE" != "development" && "$MODE" != "production" ]]; then
        error "Mode must be 'development' or 'production'"
    fi
    
    # Validate production requirements
    if [[ "$MODE" == "production" && -z "$EMAIL" ]]; then
        error "Email is required for production mode"
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    local deps=("openssl")
    
    if [[ "$MODE" == "production" ]]; then
        deps+=("certbot")
    fi
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            if [[ "$dep" == "certbot" ]]; then
                log "Installing certbot..."
                install_certbot
            else
                error "Required dependency '$dep' is not installed"
            fi
        fi
    done
    
    success "All dependencies are available"
}

# Install certbot for Let's Encrypt
install_certbot() {
    log "Installing certbot..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y certbot
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot
    elif command -v brew &> /dev/null; then
        brew install certbot
    else
        error "Unable to install certbot. Please install manually."
    fi
    
    success "Certbot installed successfully"
}

# Setup SSL directory structure
setup_ssl_directories() {
    log "Setting up SSL directory structure..."
    
    # Create local SSL directory
    mkdir -p "$SSL_DIR"
    
    # Create system SSL directories (with sudo)
    if [[ ! -d "$CERT_DIR" ]]; then
        sudo mkdir -p "$CERT_DIR"
    fi
    
    if [[ ! -d "$KEY_DIR" ]]; then
        sudo mkdir -p "$KEY_DIR"
    fi
    
    # Set proper permissions
    sudo chmod 755 "$CERT_DIR"
    sudo chmod 700 "$KEY_DIR"
    
    success "SSL directories created"
}

# Generate self-signed certificate for development
generate_self_signed() {
    log "Generating self-signed SSL certificate for development..."
    
    local key_file="${SSL_DIR}/jobbot.key"
    local cert_file="${SSL_DIR}/jobbot.crt"
    local csr_file="${SSL_DIR}/jobbot.csr"
    
    # Generate private key
    openssl genrsa -out "$key_file" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$key_file" -out "$csr_file" -subj "/C=US/ST=CA/L=San Francisco/O=JobBot/OU=Development/CN=$DOMAIN"
    
    # Generate self-signed certificate (valid for 1 year)
    openssl x509 -req -days 365 -in "$csr_file" -signkey "$key_file" -out "$cert_file"
    
    # Set proper permissions
    chmod 600 "$key_file"
    chmod 644 "$cert_file"
    
    # Clean up CSR
    rm "$csr_file"
    
    # Copy to system directories
    sudo cp "$cert_file" "$CERT_DIR/jobbot.crt"
    sudo cp "$key_file" "$KEY_DIR/jobbot.key"
    sudo chmod 644 "$CERT_DIR/jobbot.crt"
    sudo chmod 600 "$KEY_DIR/jobbot.key"
    
    success "Self-signed certificate generated and installed"
    warn "This certificate is for development only and will show browser warnings"
}

# Generate Let's Encrypt certificate for production
generate_letsencrypt() {
    log "Generating Let's Encrypt SSL certificate for production..."
    
    # Stop any running nginx to allow certbot to bind to port 80
    log "Stopping nginx temporarily for certificate generation..."
    docker-compose -f docker-compose.prod.yml stop nginx || true
    
    # Generate certificate using certbot standalone mode
    sudo certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --keep-until-expiring \
        --expand
    
    # Copy certificates to our SSL directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/jobbot.crt"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/jobbot.key"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/jobbot-chain.crt"
    
    # Set proper permissions
    sudo chmod 644 "$SSL_DIR/jobbot.crt"
    sudo chmod 600 "$SSL_DIR/jobbot.key"
    sudo chmod 644 "$SSL_DIR/jobbot-chain.crt"
    
    # Copy to system directories
    sudo cp "$SSL_DIR/jobbot.crt" "$CERT_DIR/jobbot.crt"
    sudo cp "$SSL_DIR/jobbot.key" "$KEY_DIR/jobbot.key"
    sudo cp "$SSL_DIR/jobbot-chain.crt" "$CERT_DIR/jobbot-chain.crt"
    
    success "Let's Encrypt certificate generated and installed"
}

# Setup automatic certificate renewal
setup_auto_renewal() {
    if [[ "$MODE" == "production" ]]; then
        log "Setting up automatic certificate renewal..."
        
        # Create renewal script
        local renewal_script="/usr/local/bin/renew-jobbot-ssl.sh"
        
        sudo tee "$renewal_script" > /dev/null << EOF
#!/bin/bash
# JobBot SSL Certificate Renewal Script

# Renew certificate
certbot renew --quiet --no-self-upgrade

# Check if renewal was successful
if [ \$? -eq 0 ]; then
    # Copy renewed certificates
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/jobbot.crt"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/jobbot.key"
    cp "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$SSL_DIR/jobbot-chain.crt"
    
    # Copy to system directories
    cp "$SSL_DIR/jobbot.crt" "$CERT_DIR/jobbot.crt"
    cp "$SSL_DIR/jobbot.key" "$KEY_DIR/jobbot.key"
    cp "$SSL_DIR/jobbot-chain.crt" "$CERT_DIR/jobbot-chain.crt"
    
    # Set proper permissions
    chmod 644 "$CERT_DIR/jobbot.crt"
    chmod 600 "$KEY_DIR/jobbot.key"
    chmod 644 "$CERT_DIR/jobbot-chain.crt"
    
    # Reload nginx
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
    
    echo "[$(date)] SSL certificate renewed successfully"
else
    echo "[$(date)] SSL certificate renewal failed"
    exit 1
fi
EOF
        
        sudo chmod +x "$renewal_script"
        
        # Add cron job for automatic renewal (runs twice daily)
        (sudo crontab -l 2>/dev/null; echo "0 2,14 * * * $renewal_script >> /var/log/ssl-renewal.log 2>&1") | sudo crontab -
        
        success "Automatic renewal configured"
        log "Certificate will be automatically renewed twice daily"
    else
        log "Skipping auto-renewal setup for development mode"
    fi
}

# Validate certificate
validate_certificate() {
    log "Validating SSL certificate..."
    
    local cert_file="$SSL_DIR/jobbot.crt"
    local key_file="$SSL_DIR/jobbot.key"
    
    if [[ ! -f "$cert_file" ]]; then
        error "Certificate file not found: $cert_file"
    fi
    
    if [[ ! -f "$key_file" ]]; then
        error "Private key file not found: $key_file"
    fi
    
    # Check certificate validity
    if ! openssl x509 -in "$cert_file" -noout -checkend 86400; then
        warn "Certificate will expire within 24 hours"
    fi
    
    # Check certificate and key match
    cert_hash=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5)
    key_hash=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5)
    
    if [[ "$cert_hash" != "$key_hash" ]]; then
        error "Certificate and private key do not match"
    fi
    
    # Display certificate information
    log "Certificate Information:"
    openssl x509 -in "$cert_file" -noout -subject -issuer -dates
    
    success "Certificate validation completed"
}

# Update environment file with SSL paths
update_environment() {
    log "Updating environment configuration..."
    
    local env_file=".env.production"
    
    if [[ -f "$env_file" ]]; then
        # Update SSL paths in environment file
        sed -i "s|SSL_CERT_PATH=.*|SSL_CERT_PATH=$CERT_DIR/jobbot.crt|g" "$env_file"
        sed -i "s|SSL_KEY_PATH=.*|SSL_KEY_PATH=$KEY_DIR/jobbot.key|g" "$env_file"
        
        if [[ "$MODE" == "production" ]]; then
            sed -i "s|SSL_CHAIN_PATH=.*|SSL_CHAIN_PATH=$CERT_DIR/jobbot-chain.crt|g" "$env_file"
        fi
        
        success "Environment file updated"
    else
        warn "Environment file not found: $env_file"
    fi
}

# Display setup summary
show_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   SSL Certificate Setup Complete${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Configuration:${NC}"
    echo "  Mode: $MODE"
    echo "  Domain: $DOMAIN"
    echo "  Certificate: $CERT_DIR/jobbot.crt"
    echo "  Private Key: $KEY_DIR/jobbot.key"
    
    if [[ "$MODE" == "production" ]]; then
        echo "  Certificate Chain: $CERT_DIR/jobbot-chain.crt"
        echo "  Auto-renewal: Enabled (twice daily)"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update nginx configuration with your domain name"
    echo "2. Start/restart nginx service:"
    echo -e "   ${BLUE}docker-compose -f docker-compose.prod.yml up -d nginx${NC}"
    echo "3. Test HTTPS connection:"
    echo -e "   ${BLUE}curl -I https://$DOMAIN/health${NC}"
    
    if [[ "$MODE" == "development" ]]; then
        echo ""
        echo -e "${RED}DEVELOPMENT WARNING:${NC}"
        echo "Self-signed certificate will show browser warnings"
        echo "Accept the certificate in your browser to proceed"
    fi
    
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "   JobBot SSL Certificate Setup"
    echo "========================================"
    echo -e "${NC}"
    
    parse_args "$@"
    check_dependencies
    setup_ssl_directories
    
    if [[ "$MODE" == "development" ]]; then
        generate_self_signed
    else
        generate_letsencrypt
    fi
    
    setup_auto_renewal
    validate_certificate
    update_environment
    show_summary
}

# Run main function
main "$@"