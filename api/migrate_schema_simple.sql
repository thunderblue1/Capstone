-- CuriousBooks Database Migration Script (Simple Version)
-- This script safely migrates from previous schema to new schema
-- It checks for column existence before adding them
-- 
-- Usage: mysql -u your_user -p your_database < migrate_schema_simple.sql
-- Or execute in MySQL Workbench, phpMyAdmin, etc.
--
-- IMPORTANT: Backup your database before running this script!

-- ============================================
-- USERS TABLE MIGRATIONS
-- ============================================

-- Add first_name if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(255) NULL AFTER password_hash;

-- Add last_name if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_name VARCHAR(255) NULL AFTER first_name;

-- Rename password to password_hash if password exists and password_hash doesn't
-- Note: This will fail if password_hash already exists, which is fine
-- Uncomment and modify if needed:
-- ALTER TABLE users CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL;

-- ============================================
-- CATEGORIES TABLE MIGRATIONS
-- ============================================

-- Add parent_id if it doesn't exist
ALTER TABLE categories 
ADD COLUMN IF NOT EXISTS parent_id INT NULL AFTER name;

-- Add index and foreign key for parent_id (will fail if already exists, which is fine)
-- Note: You may need to run these separately if the column was just added
-- ALTER TABLE categories ADD INDEX IF NOT EXISTS idx_parent_id (parent_id);
-- ALTER TABLE categories ADD CONSTRAINT fk_category_parent 
--   FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL;

-- ============================================
-- REVIEWS TABLE MIGRATIONS
-- ============================================

-- Change rating from INT to FLOAT (if it's currently INT)
-- Note: This will preserve existing data
ALTER TABLE reviews 
MODIFY COLUMN rating FLOAT NOT NULL;

-- Add index if it doesn't exist
ALTER TABLE reviews 
ADD INDEX IF NOT EXISTS idx_reviews_book (book_id);

-- ============================================
-- ORDERS TABLE MIGRATIONS
-- ============================================

-- Add Stripe payment fields
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(255) NULL AFTER updated_at;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255) NULL AFTER stripe_payment_intent_id;

-- Add customer information fields
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS customer_email VARCHAR(150) NULL AFTER stripe_customer_id;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255) NULL AFTER customer_email;

-- Add shipping address fields
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_address_line1 VARCHAR(255) NULL AFTER customer_name;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_address_line2 VARCHAR(255) NULL AFTER shipping_address_line1;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_city VARCHAR(100) NULL AFTER shipping_address_line2;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_state VARCHAR(50) NULL AFTER shipping_city;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_postal_code VARCHAR(20) NULL AFTER shipping_state;

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS shipping_country VARCHAR(50) NULL AFTER shipping_postal_code;

-- Add index for stripe_payment_intent_id if it doesn't exist
ALTER TABLE orders 
ADD INDEX IF NOT EXISTS idx_stripe_payment_intent_id (stripe_payment_intent_id);

-- ============================================
-- ORDER_ITEMS TABLE MIGRATIONS
-- ============================================

-- Add index if it doesn't exist
ALTER TABLE order_items 
ADD INDEX IF NOT EXISTS idx_orderitems_book (book_id);

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT 'Migration script completed!';
SELECT 'Note: Some statements may show errors if columns/indexes already exist - this is normal.';
SELECT 'Please verify your schema matches the new schema in database_schema.sql';

