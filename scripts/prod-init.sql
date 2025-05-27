-- JobBot Production Database Initialization Script
-- Secure PostgreSQL configuration for production deployment

-- ========================================
-- Security Configuration
-- ========================================

-- Create application user with limited privileges
CREATE USER IF NOT EXISTS jobbot_app WITH PASSWORD 'CHANGEME_APP_PASSWORD';

-- Create read-only user for monitoring and analytics
CREATE USER IF NOT EXISTS jobbot_readonly WITH PASSWORD 'CHANGEME_READONLY_PASSWORD';

-- Create backup user for database backup operations
CREATE USER IF NOT EXISTS jobbot_backup WITH PASSWORD 'CHANGEME_BACKUP_PASSWORD';

-- ========================================
-- Database Setup
-- ========================================

-- Ensure proper encoding and collation
ALTER DATABASE jobbot_prod SET timezone TO 'UTC';
ALTER DATABASE jobbot_prod SET default_text_search_config TO 'english';

-- ========================================
-- Extensions
-- ========================================

-- UUID support for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enhanced text search capabilities
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- JSON query optimization
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Statistics for query optimization
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Row-level security
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========================================
-- Performance Tuning
-- ========================================

-- Connection pooling settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Write-ahead logging for performance
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET checkpoint_timeout = '10min';

-- Query optimization
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- ========================================
-- Security Configuration
-- ========================================

-- Enable row-level security by default
ALTER DATABASE jobbot_prod SET row_security = on;

-- Enable SSL requirement
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';

-- Logging for security monitoring
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- ========================================
-- Backup Configuration
-- ========================================

-- Enable point-in-time recovery
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /backups/archive/%f';
ALTER SYSTEM SET wal_level = replica;

-- ========================================
-- User Privileges
-- ========================================

-- Application user permissions
GRANT CONNECT ON DATABASE jobbot_prod TO jobbot_app;
GRANT USAGE, CREATE ON SCHEMA public TO jobbot_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jobbot_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jobbot_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jobbot_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jobbot_app;

-- Read-only user permissions (for monitoring)
GRANT CONNECT ON DATABASE jobbot_prod TO jobbot_readonly;
GRANT USAGE ON SCHEMA public TO jobbot_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO jobbot_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO jobbot_readonly;

-- Backup user permissions
GRANT CONNECT ON DATABASE jobbot_prod TO jobbot_backup;
GRANT USAGE ON SCHEMA public TO jobbot_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO jobbot_backup;
GRANT pg_read_all_data TO jobbot_backup;

-- ========================================
-- Monitoring Setup
-- ========================================

-- Create monitoring schema
CREATE SCHEMA IF NOT EXISTS monitoring;
GRANT USAGE ON SCHEMA monitoring TO jobbot_readonly;

-- Performance monitoring view
CREATE OR REPLACE VIEW monitoring.query_performance AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC;

GRANT SELECT ON monitoring.query_performance TO jobbot_readonly;

-- Database size monitoring
CREATE OR REPLACE VIEW monitoring.database_size AS
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size,
    pg_database_size(datname) as size_bytes
FROM pg_database
WHERE datname = current_database();

GRANT SELECT ON monitoring.database_size TO jobbot_readonly;

-- Connection monitoring
CREATE OR REPLACE VIEW monitoring.connections AS
SELECT 
    state,
    count(*) as count,
    max(now() - state_change) as max_duration
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;

GRANT SELECT ON monitoring.connections TO jobbot_readonly;

-- ========================================
-- Health Check Function
-- ========================================

CREATE OR REPLACE FUNCTION monitoring.health_check()
RETURNS json AS $$
DECLARE
    result json;
BEGIN
    SELECT json_build_object(
        'database', current_database(),
        'timestamp', now(),
        'uptime', date_trunc('second', now() - pg_postmaster_start_time()),
        'connections', (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()),
        'database_size', pg_size_pretty(pg_database_size(current_database())),
        'cache_hit_ratio', (
            SELECT round(100.0 * sum(blks_hit) / nullif(sum(blks_hit + blks_read), 0), 2)
            FROM pg_stat_database
            WHERE datname = current_database()
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION monitoring.health_check() TO jobbot_readonly;

-- ========================================
-- Reload Configuration
-- ========================================

-- Apply configuration changes
SELECT pg_reload_conf();

-- ========================================
-- Production Notes
-- ========================================

/*
IMPORTANT SECURITY NOTES:

1. Change all default passwords:
   - CHANGEME_APP_PASSWORD
   - CHANGEME_READONLY_PASSWORD  
   - CHANGEME_BACKUP_PASSWORD

2. SSL Certificate Setup:
   - Place server.crt in /etc/ssl/certs/
   - Place server.key in /etc/ssl/private/
   - Ensure proper permissions (600 for key file)

3. Backup Configuration:
   - Ensure /backups/archive directory exists with proper permissions
   - Set up regular backup monitoring and testing

4. Connection Configuration:
   - Update pg_hba.conf for SSL-only connections
   - Configure connection pooling (PgBouncer recommended)

5. Monitoring Setup:
   - Monitor query performance via monitoring.query_performance
   - Set up alerts for connection limits and disk space
   - Regular monitoring of cache hit ratios

6. Regular Maintenance:
   - Schedule VACUUM ANALYZE operations
   - Monitor index usage and optimize as needed
   - Regular security updates and patches
*/