# JobBot Business Intelligence Dashboard
# Multi-stage Dockerfile for React frontend with Nginx

# ===============================================
# Stage 1: Build Dependencies
# ===============================================
FROM node:18-alpine as dependencies
WORKDIR /app

# Copy package files for dependency caching
COPY package*.json ./

# Install dependencies with clean cache
RUN npm ci --only=production && \
    npm cache clean --force

# ===============================================
# Stage 2: Development Dependencies
# ===============================================
FROM node:18-alpine as dev-dependencies
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies including dev dependencies
RUN npm ci && \
    npm cache clean --force

# ===============================================
# Stage 3: Build Application
# ===============================================
FROM dev-dependencies as builder
WORKDIR /app

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./
COPY vite.config.js ./

# Set build environment
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Verify build output
RUN ls -la dist/

# ===============================================
# Stage 4: Production Server
# ===============================================
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]