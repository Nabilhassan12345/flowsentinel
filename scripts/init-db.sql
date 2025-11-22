-- ============================================================================
-- FlowSentinel Database Initialization Script
-- ============================================================================
-- This script is automatically executed when PostgreSQL container starts
-- It sets up the database schema and initial configuration
-- ============================================================================

-- Create extensions (if needed in future)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE flowsentinel TO flowsentinel;

-- Note: Tables will be created automatically by SQLAlchemy on first run
-- This script is for any additional setup or seed data

-- Optional: Create read-only user for analytics
-- CREATE USER flowsentinel_readonly WITH PASSWORD 'readonly123';
-- GRANT CONNECT ON DATABASE flowsentinel TO flowsentinel_readonly;
-- GRANT USAGE ON SCHEMA public TO flowsentinel_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO flowsentinel_readonly;

