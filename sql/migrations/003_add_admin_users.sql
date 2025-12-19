-- ============================================================================
-- Migration: Add Admin Users Table
-- Date: 2025-12-18
-- Description: Adds admin_users table for authentication
-- ============================================================================

BEGIN;

-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for username lookup
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);

-- Insert default admin user
-- Password: TKsltk#123 (hashed with bcrypt)
-- Note: This hash is generated using bcrypt with default rounds
INSERT INTO admin_users (username, password_hash)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTJlZVhW0RqKXe')
ON CONFLICT (username) DO NOTHING;

COMMIT;

-- Verify
SELECT username, created_at FROM admin_users;
