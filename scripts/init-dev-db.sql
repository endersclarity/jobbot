-- JobBot Development Database Initialization
-- Sets up development database with proper permissions and extensions

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create development schema
CREATE SCHEMA IF NOT EXISTS jobbot_dev;

-- Grant permissions to jobbot_user
GRANT ALL PRIVILEGES ON SCHEMA jobbot_dev TO jobbot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA jobbot_dev TO jobbot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA jobbot_dev TO jobbot_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA jobbot_dev GRANT ALL ON TABLES TO jobbot_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA jobbot_dev GRANT ALL ON SEQUENCES TO jobbot_user;

-- Create indexes for common queries (will be created by Alembic but good for reference)
-- These will be created automatically by the application migrations

-- Sample development data (optional)
-- This will be populated by the application's development seed data