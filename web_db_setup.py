# web_db_setup.py
from dotenv import load_dotenv
import psycopg2
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

def setup_database():
    logging.info("Starting database setup...")
    try:
        # Get the database URL from the environment variable
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable not set")

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Existing tables (ensure they are defined as in parsing.py)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iphones_catalog (
                id SERIAL PRIMARY KEY,
                product_id TEXT UNIQUE,
                model TEXT NOT NULL,
                price INTEGER DEFAULT 0,
                currency TEXT DEFAULT 'RUB',
                old_price TEXT,
                current_color TEXT,
                current_memory TEXT,
                current_sim TEXT,
                image_url TEXT,
                product_url TEXT,
                parsed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT, -- Added category for filtering
                is_featured INTEGER DEFAULT 0, -- For featured products
                display_order INTEGER DEFAULT 0 -- For sorting
            )
        ''')
        logging.info("iphones_catalog table created or already exists.")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iphone_catalog_colors (
                id SERIAL PRIMARY KEY,
                product_id TEXT,
                color_name TEXT
            )
        ''')
        logging.info("iphone_catalog_colors table created or already exists.")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iphone_catalog_memory (
                id SERIAL PRIMARY KEY,
                product_id TEXT,
                memory_size TEXT
            )
        ''')
        logging.info("iphone_catalog_memory table created or already exists.")

        # New table for orders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                product_id TEXT NOT NULL,
                price INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                charge_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logging.info("orders table created or already exists.")
        
        conn.commit()
        conn.close()
        logging.info("Database setup complete.")
    except Exception as e:
        logging.error(f"An error occurred during database setup: {e}")
        raise

if __name__ == '__main__':
    setup_database()