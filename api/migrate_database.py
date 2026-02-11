"""
Database Migration Script for CuriousBooks
Safely migrates from previous schema to new schema

Usage:
    python migrate_database.py
    
Or with custom database connection:
    python migrate_database.py --host localhost --user root --password yourpass --database curiousbooks
"""
import sys
import os
import argparse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config


def column_exists(inspector, table_name, column_name):
    """Check if a column exists in a table"""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(inspector, table_name, index_name):
    """Check if an index exists in a table"""
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def migrate_database(connection_string=None, database_name=None):
    """Perform database migration"""
    
    if connection_string:
        engine = create_engine(connection_string)
    else:
        # Use config from config.py
        config_obj = config['development']
        database_uri = config_obj.SQLALCHEMY_DATABASE_URI
        engine = create_engine(database_uri)
    
    inspector = inspect(engine)
    
    print("=" * 60)
    print("CuriousBooks Database Migration")
    print("=" * 60)
    print()
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # ============================================
            # USERS TABLE MIGRATIONS
            # ============================================
            print("Migrating users table...")
            
            if not column_exists(inspector, 'users', 'first_name'):
                conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(255) NULL AFTER password_hash"))
                print("  ✓ Added first_name column")
            else:
                print("  - first_name column already exists")
            
            if not column_exists(inspector, 'users', 'last_name'):
                conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(255) NULL AFTER first_name"))
                print("  ✓ Added last_name column")
            else:
                print("  - last_name column already exists")
            
            # Check if password needs to be renamed to password_hash
            if column_exists(inspector, 'users', 'password') and not column_exists(inspector, 'users', 'password_hash'):
                conn.execute(text("ALTER TABLE users CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL"))
                print("  ✓ Renamed password to password_hash")
            elif column_exists(inspector, 'users', 'password_hash'):
                print("  - password_hash column already exists")
            
            # ============================================
            # CATEGORIES TABLE MIGRATIONS
            # ============================================
            print("\nMigrating categories table...")
            
            if not column_exists(inspector, 'categories', 'parent_id'):
                conn.execute(text("ALTER TABLE categories ADD COLUMN parent_id INT NULL AFTER name"))
                print("  ✓ Added parent_id column")
                
                # Add index
                conn.execute(text("ALTER TABLE categories ADD INDEX idx_parent_id (parent_id)"))
                print("  ✓ Added idx_parent_id index")
                
                # Add foreign key
                try:
                    conn.execute(text("""
                        ALTER TABLE categories 
                        ADD CONSTRAINT fk_category_parent 
                        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
                    """))
                    print("  ✓ Added foreign key constraint")
                except ProgrammingError as e:
                    if "Duplicate foreign key" not in str(e):
                        raise
                    print("  - Foreign key already exists")
            else:
                print("  - parent_id column already exists")
            
            # ============================================
            # REVIEWS TABLE MIGRATIONS
            # ============================================
            print("\nMigrating reviews table...")
            
            # Check rating type and convert if needed
            columns = inspector.get_columns('reviews')
            rating_col = next((col for col in columns if col['name'] == 'rating'), None)
            if rating_col and str(rating_col['type']).upper() in ['INTEGER', 'INT', 'TINYINT']:
                conn.execute(text("ALTER TABLE reviews MODIFY COLUMN rating FLOAT NOT NULL"))
                print("  ✓ Changed rating from INT to FLOAT")
            else:
                print("  - rating column is already FLOAT")
            
            if not index_exists(inspector, 'reviews', 'idx_reviews_book'):
                conn.execute(text("ALTER TABLE reviews ADD INDEX idx_reviews_book (book_id)"))
                print("  ✓ Added idx_reviews_book index")
            else:
                print("  - idx_reviews_book index already exists")
            
            # ============================================
            # ORDERS TABLE MIGRATIONS
            # ============================================
            print("\nMigrating orders table...")
            
            # Stripe fields
            if not column_exists(inspector, 'orders', 'stripe_payment_intent_id'):
                conn.execute(text("ALTER TABLE orders ADD COLUMN stripe_payment_intent_id VARCHAR(255) NULL AFTER updated_at"))
                print("  ✓ Added stripe_payment_intent_id column")
            else:
                print("  - stripe_payment_intent_id column already exists")
            
            if not column_exists(inspector, 'orders', 'stripe_customer_id'):
                conn.execute(text("ALTER TABLE orders ADD COLUMN stripe_customer_id VARCHAR(255) NULL AFTER stripe_payment_intent_id"))
                print("  ✓ Added stripe_customer_id column")
            else:
                print("  - stripe_customer_id column already exists")
            
            # Customer info fields
            customer_fields = [
                ('customer_email', 'VARCHAR(150)'),
                ('customer_name', 'VARCHAR(255)'),
            ]
            
            for field_name, field_type in customer_fields:
                if not column_exists(inspector, 'orders', field_name):
                    after_col = 'stripe_customer_id' if field_name == 'customer_email' else 'customer_email'
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {field_name} {field_type} NULL AFTER {after_col}"))
                    print(f"  ✓ Added {field_name} column")
                else:
                    print(f"  - {field_name} column already exists")
            
            # Shipping address fields
            shipping_fields = [
                ('shipping_address_line1', 'VARCHAR(255)'),
                ('shipping_address_line2', 'VARCHAR(255)'),
                ('shipping_city', 'VARCHAR(100)'),
                ('shipping_state', 'VARCHAR(50)'),
                ('shipping_postal_code', 'VARCHAR(20)'),
                ('shipping_country', 'VARCHAR(50)'),
            ]
            
            for i, (field_name, field_type) in enumerate(shipping_fields):
                if not column_exists(inspector, 'orders', field_name):
                    after_col = 'customer_name' if i == 0 else shipping_fields[i-1][0]
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {field_name} {field_type} NULL AFTER {after_col}"))
                    print(f"  ✓ Added {field_name} column")
                else:
                    print(f"  - {field_name} column already exists")
            
            # Add index for stripe_payment_intent_id
            if not index_exists(inspector, 'orders', 'idx_stripe_payment_intent_id'):
                conn.execute(text("ALTER TABLE orders ADD INDEX idx_stripe_payment_intent_id (stripe_payment_intent_id)"))
                print("  ✓ Added idx_stripe_payment_intent_id index")
            else:
                print("  - idx_stripe_payment_intent_id index already exists")
            
            # ============================================
            # ORDER_ITEMS TABLE MIGRATIONS
            # ============================================
            print("\nMigrating order_items table...")
            
            if not index_exists(inspector, 'order_items', 'idx_orderitems_book'):
                conn.execute(text("ALTER TABLE order_items ADD INDEX idx_orderitems_book (book_id)"))
                print("  ✓ Added idx_orderitems_book index")
            else:
                print("  - idx_orderitems_book index already exists")
            
            # Commit transaction
            trans.commit()
            
            print("\n" + "=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error during migration: {e}")
            print("Transaction rolled back. No changes were made.")
            raise


def main():
    parser = argparse.ArgumentParser(description='Migrate CuriousBooks database schema')
    parser.add_argument('--host', default=None, help='Database host')
    parser.add_argument('--user', default=None, help='Database user')
    parser.add_argument('--password', default=None, help='Database password')
    parser.add_argument('--database', default=None, help='Database name')
    parser.add_argument('--port', type=int, default=3306, help='Database port')
    
    args = parser.parse_args()
    
    if args.host and args.user and args.database:
        # Build connection string from arguments
        password_part = f":{args.password}" if args.password else ""
        connection_string = f"mysql+pymysql://{args.user}{password_part}@{args.host}:{args.port}/{args.database}"
        migrate_database(connection_string=connection_string)
    else:
        # Use config from config.py
        migrate_database()


if __name__ == '__main__':
    main()

