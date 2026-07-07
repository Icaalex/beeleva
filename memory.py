import sqlite3
from datetime import datetime
from database import get_connection


def get_customer_memory(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM memory WHERE customer_email = ?
    """, (email,))
    
    
    row = cursor.fetchone()
    
    
    conn.close()
    
    if row:
        return dict(row)
       
    return None
    

def save_customer_memory(email: str, summary: str):
   
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO memory (customer_email, summary, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(customer_email) DO UPDATE SET
            summary = excluded.summary,
            last_updated = excluded.last_updated
    """, (email, summary, datetime.now().isoformat()))
    
    
    conn.commit()
    conn.close()
    print(f"Memory saved for {email}")

def get_or_create_customer(email: str, name: str = None, phone: str = None):
    # This checks if a customer exists in our customers table
    # If yes — returns their record
    # If no — creates them first, then returns their record
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
    customer = cursor.fetchone()
    
    if not customer:
        # New customer — add them to the database
        cursor.execute("""
            INSERT INTO customers (name, email, phone, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, datetime.now().isoformat()))
        conn.commit()
        print(f"New customer created: {email}")
    
    cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
    customer = cursor.fetchone()
    conn.close()
    
    return dict(customer)