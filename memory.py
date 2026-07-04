import sqlite3
from datetime import datetime
from database import get_connection

# This file handles everything related to Beeleva's memory
# Think of it like a customer file cabinet —
# before responding to anyone, Beeleva checks this cabinet first

def get_customer_memory(email: str):
    # This function looks up what Beeleva remembers about a customer
    # It takes their email as the search key
    # Returns their memory summary if found, or None if they're new
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM memory WHERE customer_email = ?
    """, (email,))
    # The ? is a placeholder — it's safer than putting the email directly
    # in the string. Prevents something called SQL injection attacks.
    
    row = cursor.fetchone()
    # fetchone() grabs just the first matching result
    # since emails are unique, there's only ever one match anyway
    
    conn.close()
    
    if row:
        return dict(row)
        # dict(row) converts the database row into a normal Python dictionary
        # so we can access it like memory["summary"]
    return None
    # None means this customer is brand new — no memory yet

def save_customer_memory(email: str, summary: str):
    # This function saves or updates what Beeleva knows about a customer
    # Called after every interaction so memory stays current
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO memory (customer_email, summary, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(customer_email) DO UPDATE SET
            summary = excluded.summary,
            last_updated = excluded.last_updated
    """, (email, summary, datetime.now().isoformat()))
    # INSERT OR UPDATE in one clean move —
    # if the customer already has a memory, it updates it
    # if they're new, it creates a fresh memory entry
    # isoformat() saves the time as a readable string like "2026-07-01T10:30:00"
    
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