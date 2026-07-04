import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from database import get_connection
from datetime import datetime

load_dotenv()
# smtplib is Python's built-in email sending library — no installation needed
# MIME is the format emails are written in — MIMEMultipart is the envelope,
# MIMEText is the letter inside it

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# Reading credentials from .env — never hardcoded

def send_email(to_email: str, subject: str, body: str):
    # This function sends a real email to a customer
    # to_email = who receives it
    # subject = email subject line
    # body = the actual message content
    
    try:
        # Create the email structure
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach the body text to the email envelope
        msg.attach(MIMEText(body, "plain"))
        # "plain" means plain text — no HTML formatting yet
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        # 587 is Gmail's standard port for sending emails securely
        
        server.starttls()
        # starttls() encrypts the connection
        # without this, emails travel as plain readable text — unsafe
        
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        # Login to Gmail using our app password
        
        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        
        print(f"Email sent to {to_email}")
        return True
    
    except Exception as e:
        # If anything goes wrong, print the error but don't crash Beeleva
        print(f"Email failed: {e}")
        return False

def log_inquiry(customer_email: str, message: str, intent: str, response: str):
    # This saves every inquiry and Beeleva's response to the database
    # So the business owner can see a full history of all interactions
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO inquiries (customer_email, message, intent, response, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_email, message, intent, response, "responded", datetime.now().isoformat()))
    # status is set to "responded" immediately since Beeleva already replied
    
    conn.commit()
    conn.close()
    print(f"Inquiry logged for {customer_email}")

def get_all_inquiries():
    # This fetches all inquiries for the dashboard
    # The business owner sees every conversation in one place
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM inquiries ORDER BY created_at DESC
    """)
    # DESC means newest first — most recent inquiries at the top
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
    # Converts each database row into a dictionary
    # and returns a list of all of them

if __name__ == "__main__":
    # Quick test — sends a real email to yourself
    send_email(
        to_email=GMAIL_ADDRESS,
        subject="Beeleva Test Email",
        body="If you're reading this, Beeleva's email system is working perfectly."
    )