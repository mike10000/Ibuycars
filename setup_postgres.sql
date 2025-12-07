-- PostgreSQL Database Setup Script for iBuyCars
-- Run this script as the postgres superuser

-- Create database
CREATE DATABASE ibuycars_db;

-- Create user with password
CREATE USER ibuycars_user WITH PASSWORD 'ibuycars_secure_2024';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE ibuycars_db TO ibuycars_user;

-- Connect to the database (in psql, use: \c ibuycars_db)
-- Then grant schema privileges
-- GRANT ALL ON SCHEMA public TO ibuycars_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ibuycars_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ibuycars_user;

-- For PostgreSQL 15+, you may also need:
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ibuycars_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ibuycars_user;
