from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import InquiryRequest, InquiryResponse
from agent import process_inquiry
from tools import send_email, log_inquiry, get_all_inquiries
from memory import get_customer_memory, get_or_create_customer
from database import init_db
import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI creates our web server
# Think of it as the front door of Beeleva —
# everything comes in and goes out through here
app = FastAPI(
    title="Beeleva 0.1",
    description="AI-powered business operator for small businesses",
    version="0.1.0"
)

# CORS allows our frontend (React) to talk to this backend
# Without this, browsers block requests between different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This runs once when the server starts — sets up the database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Beeleva is online.")
    yield

app = FastAPI(
    title="Beeleva 0.1",
    description="AI-powered business operator for small businesses",
    version="0.1.0",
    lifespan=lifespan
)

# ROUTE 1: Health check
# A simple endpoint to confirm the server is running
@app.get("/")
async def root():
    return {"status": "Beeleva 0.1 is online", "ready": True}

# ROUTE 2: Main inquiry endpoint
# This is the core of Beeleva — where customer messages come in
@app.post("/inquiry", response_model=InquiryResponse)
async def handle_inquiry(request: InquiryRequest):
    # request is automatically validated by Pydantic before reaching here
    # if email is invalid or name is missing, FastAPI rejects it before this runs
    
    try:
        # Check if returning customer before processing
        existing_memory = get_customer_memory(request.email)
        is_returning = existing_memory is not None
        # is_returning = True means we have memory of them
        
        # Send to Beeleva's brain for processing
        ai_response = process_inquiry(
            email=request.email,
            name=request.name,
            message=request.message
        )
        
        # Log the inquiry to database
        log_inquiry(
            customer_email=request.email,
            message=request.message,
            intent="inquiry",
            response=ai_response
        )
        
        # Send the response to the customer's email automatically
        send_email(
            to_email=request.email,
            subject=f"Re: Your inquiry to Beeleva",
            body=ai_response
        )
        
        return InquiryResponse(
            status="success",
            message=ai_response,
            customer_email=request.email,
            is_returning_customer=is_returning
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        # If anything breaks, return a clean error instead of crashing

# ROUTE 3: Get all inquiries for dashboard
@app.get("/inquiries")
async def get_inquiries():
    return get_all_inquiries()

# ROUTE 4: Get customer memory
@app.get("/memory/{email}")
async def get_memory(email: str):
    memory = get_customer_memory(email)
    if not memory:
        return {"message": "No memory found for this customer"}
    return memory