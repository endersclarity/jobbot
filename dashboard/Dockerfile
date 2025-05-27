# JobBot React Dashboard - Production Dockerfile
# Multi-stage build for optimized frontend deployment

# ========================================
# Stage 1: Base Node Environment
# ========================================
FROM node:18-alpine as base

# Set environment variables
ENV NODE_ENV=production \
    NPM_CONFIG_LOGLEVEL=warn \
    NPM_CONFIG_COLOR=false

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    && rm -rf /var/cache/apk/*

# Create app user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactuser -u 1001

# Set work directory
WORKDIR /app

# ========================================
# Stage 2: Dependencies Installation
# ========================================
FROM base as dependencies

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# ========================================
# Stage 3: Build Stage
# ========================================
FROM dependencies as builder

# Install all dependencies including dev dependencies
RUN npm ci

# Copy source code
COPY public/ ./public/
COPY src/ ./src/
COPY index.html .
COPY vite.config.js .

# Build application
RUN npm run build

# ========================================
# Stage 4: Production Image
# ========================================
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY --from=builder /app/dist /usr/share/nginx/html

# Create custom nginx configuration
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html index.htm;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml+rss;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https:; connect-src 'self' ws: wss:;";

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (if needed)
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket proxy for real-time updates
    location /ws {
        proxy_pass http://backend:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# ========================================
# Stage 5: Development Image
# ========================================
FROM dependencies as development

# Install all dependencies
RUN npm ci

# Copy source code
COPY . .

# Switch to app user
USER reactuser

# Expose development port
EXPOSE 5173

# Development command with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ========================================
# Build Arguments and Labels
# ========================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=3.0.0

LABEL maintainer="Kaelen Jennings <endersclarity@gmail.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="JobBot React Dashboard" \
      org.label-schema.description="Real-time monitoring dashboard for JobBot Business Intelligence Engine" \
      org.label-schema.url="https://github.com/endersclarity/jobbot" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/endersclarity/jobbot" \
      org.label-schema.vendor="Kaelen Jennings" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"