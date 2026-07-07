import sqlite3
from datetime import datetime

def get_connection():
    conn = sqlite3.connect("beeleva.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            created_at TEXT
        )
    """)
    
    # Inquiries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT,
            message TEXT,
            intent TEXT,
            response TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    
    # Memory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT UNIQUE,
            summary TEXT,
            last_updated TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()


