-- CuriousBooks Database Migration: Add role column to users table
-- This adds a role field for role-based access control (RBAC)
-- 
-- Usage: 
--   mysql -u your_user -p your_database < migrate_add_role_column.sql
--   Or execute in MySQL Workbench, phpMyAdmin, etc.
--
-- IMPORTANT: Backup your database before running this script!

SET @dbname = DATABASE();

-- ============================================
-- USERS TABLE: Add role column
-- ============================================

SET @tablename = "users";
SET @columnname = "role";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column role already exists in users table.' AS message",
  "ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'customer' AFTER last_name"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- USERS TABLE: Add index on role column
-- ============================================

SET @indexname = "idx_users_role";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND index_name = @indexname
  ) > 0,
  "SELECT 'Index idx_users_role already exists.' AS message",
  "ALTER TABLE users ADD INDEX idx_users_role (role)"
));
PREPARE createIndexIfNotExists FROM @preparedStatement;
EXECUTE createIndexIfNotExists;
DEALLOCATE PREPARE createIndexIfNotExists;

-- ============================================
-- Update existing users to have 'customer' role
-- ============================================

UPDATE users SET role = 'customer' WHERE role IS NULL OR role = '';

-- ============================================
-- Notes:
-- ============================================
-- To create a manager user, run:
-- UPDATE users SET role = 'manager' WHERE id = <user_id>;
--
-- To check current roles:
-- SELECT id, username, email, role FROM users;

