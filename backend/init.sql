-- Database initialization script for PR Campaign System
-- This script runs when PostgreSQL container starts up

-- Create the main database (if not exists)
SELECT 'CREATE DATABASE pr_campaign_system'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pr_campaign_system')\gexec

-- Create the test database (if not exists)  
SELECT 'CREATE DATABASE pr_campaign_system_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pr_campaign_system_test')\gexec

-- Grant permissions to postgres user (already has superuser, but being explicit)
GRANT ALL PRIVILEGES ON DATABASE pr_campaign_system TO postgres;
GRANT ALL PRIVILEGES ON DATABASE pr_campaign_system_test TO postgres;

-- Create a dedicated user for the application (optional, but good practice)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'prcs_user') THEN

      CREATE USER prcs_user WITH PASSWORD 'prcs_password';
   END IF;
END
$do$;

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON DATABASE pr_campaign_system TO prcs_user;
GRANT ALL PRIVILEGES ON DATABASE pr_campaign_system_test TO prcs_user;

-- Connect to main database and set up extensions
\c pr_campaign_system;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Connect to test database and set up extensions  
\c pr_campaign_system_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Switch back to postgres database
\c postgres; 