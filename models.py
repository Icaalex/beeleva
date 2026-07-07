from pydantic import BaseModel, EmailStr
from typing import Optional

# Pydantic models are like forms with rules
# Before any data reaches Beeleva's brain, it must pass through here
# If someone sends incomplete or wrong data, Pydantic rejects it automatically
# This protects Beeleva from crashing on bad input

class InquiryRequest(BaseModel):
    # This defines what a valid incoming inquiry looks like
    # Every field listed here is REQUIRED unless marked Optional
    
    name: str
    # Customer's name — must be a string
    
    email: EmailStr
    # EmailStr is special — Pydantic automatically checks it's a valid email format
    # "notanemail" would be rejected, "ada@gmail.com" passes
    
    message: str
    # The actual inquiry message
    
    phone: Optional[str] = None
    # Phone is optional — not everyone provides it
    # = None means if not provided, it defaults to None

class InquiryResponse(BaseModel):
    # This defines what Beeleva sends back after processing
    
    status: str
    # "success" or "error"
    
    message: str
    # Beeleva's actual response to the customer
    
    customer_email: str
    # Echo back the email so the frontend knows who was processed
    
    is_returning_customer: bool
    # True if Beeleva recognized them from memory
    # False if they're brand new
    # This is useful for the dashboard — shows memory working

class CustomerResponse(BaseModel):
    # Used when fetching customer data for the dashboard
    
    id: int
    name: Optional[str]
    email: str
    phone: Optional[str]
    created_at: str