-- CuriousBooks Database Migration Script for MySQL
-- This script safely migrates from previous schema to new schema
-- It checks for column/index existence before adding them
-- 
-- Usage: 
--   mysql -u your_user -p your_database < migrate_schema_mysql.sql
--   Or execute in MySQL Workbench, phpMyAdmin, etc.
--
-- IMPORTANT: Backup your database before running this script!

SET @dbname = DATABASE();

-- ============================================
-- USERS TABLE MIGRATIONS
-- ============================================

-- Add first_name if it doesn't exist
SET @tablename = "users";
SET @columnname = "first_name";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column first_name already exists in users table.' AS message",
  "ALTER TABLE users ADD COLUMN first_name VARCHAR(255) NULL AFTER password_hash"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add last_name if it doesn't exist
SET @columnname = "last_name";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column last_name already exists in users table.' AS message",
  "ALTER TABLE users ADD COLUMN last_name VARCHAR(255) NULL AFTER first_name"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Rename password to password_hash if password exists and password_hash doesn't
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = 'password'
  ) > 0
  AND
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = 'password_hash'
  ) = 0,
  "ALTER TABLE users CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL",
  "SELECT 'Password column migration not needed.' AS message"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- CATEGORIES TABLE MIGRATIONS
-- ============================================

SET @tablename = "categories";

-- Add parent_id if it doesn't exist
SET @columnname = "parent_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column parent_id already exists in categories table.' AS message",
  "ALTER TABLE categories ADD COLUMN parent_id INT NULL AFTER name"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add index for parent_id if it doesn't exist
SET @indexname = "idx_parent_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND index_name = @indexname
  ) > 0,
  "SELECT 'Index idx_parent_id already exists.' AS message",
  "ALTER TABLE categories ADD INDEX idx_parent_id (parent_id)"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add foreign key for parent_id if it doesn't exist
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND constraint_name = 'fk_category_parent'
  ) > 0,
  "SELECT 'Foreign key fk_category_parent already exists.' AS message",
  "ALTER TABLE categories ADD CONSTRAINT fk_category_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- REVIEWS TABLE MIGRATIONS
-- ============================================

SET @tablename = "reviews";

-- Change rating from INT to FLOAT if needed
SET @preparedStatement = (SELECT IF(
  (
    SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = 'rating'
      AND (DATA_TYPE = 'int' OR DATA_TYPE = 'tinyint' OR DATA_TYPE = 'smallint')
  ) IS NOT NULL,
  "ALTER TABLE reviews MODIFY COLUMN rating FLOAT NOT NULL",
  "SELECT 'Rating column is already FLOAT or does not exist.' AS message"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add index if it doesn't exist
SET @indexname = "idx_reviews_book";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND index_name = @indexname
  ) > 0,
  "SELECT 'Index idx_reviews_book already exists.' AS message",
  "ALTER TABLE reviews ADD INDEX idx_reviews_book (book_id)"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- ORDERS TABLE MIGRATIONS
-- ============================================

SET @tablename = "orders";

-- Add Stripe payment fields
SET @columnname = "stripe_payment_intent_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column stripe_payment_intent_id already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN stripe_payment_intent_id VARCHAR(255) NULL AFTER updated_at"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "stripe_customer_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column stripe_customer_id already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN stripe_customer_id VARCHAR(255) NULL AFTER stripe_payment_intent_id"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add customer information fields
SET @columnname = "customer_email";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column customer_email already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN customer_email VARCHAR(150) NULL AFTER stripe_customer_id"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "customer_name";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column customer_name already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(255) NULL AFTER customer_email"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add shipping address fields
SET @columnname = "shipping_address_line1";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_address_line1 already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_address_line1 VARCHAR(255) NULL AFTER customer_name"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "shipping_address_line2";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_address_line2 already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_address_line2 VARCHAR(255) NULL AFTER shipping_address_line1"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "shipping_city";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_city already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_city VARCHAR(100) NULL AFTER shipping_address_line2"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "shipping_state";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_state already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_state VARCHAR(50) NULL AFTER shipping_city"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "shipping_postal_code";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_postal_code already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_postal_code VARCHAR(20) NULL AFTER shipping_state"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @columnname = "shipping_country";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND column_name = @columnname
  ) > 0,
  "SELECT 'Column shipping_country already exists in orders table.' AS message",
  "ALTER TABLE orders ADD COLUMN shipping_country VARCHAR(50) NULL AFTER shipping_postal_code"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add index for stripe_payment_intent_id if it doesn't exist
SET @indexname = "idx_stripe_payment_intent_id";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND index_name = @indexname
  ) > 0,
  "SELECT 'Index idx_stripe_payment_intent_id already exists.' AS message",
  "ALTER TABLE orders ADD INDEX idx_stripe_payment_intent_id (stripe_payment_intent_id)"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- ORDER_ITEMS TABLE MIGRATIONS
-- ============================================

SET @tablename = "order_items";

-- Add index if it doesn't exist
SET @indexname = "idx_orderitems_book";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_name = @tablename
      AND table_schema = @dbname
      AND index_name = @indexname
  ) > 0,
  "SELECT 'Index idx_orderitems_book already exists.' AS message",
  "ALTER TABLE order_items ADD INDEX idx_orderitems_book (book_id)"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT '========================================' AS '';
SELECT 'Migration completed successfully!' AS '';
SELECT '========================================' AS '';
SELECT 'Please verify your database schema matches the new schema in database_schema.sql' AS '';

