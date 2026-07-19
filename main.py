from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from models import InquiryRequest, InquiryResponse
from agent import process_inquiry
from tools import send_email, log_inquiry, get_all_inquiries
from memory import get_customer_memory, get_or_create_customer
from database import init_db
import os
from dotenv import load_dotenv

load_dotenv()

# lifespan must be defined BEFORE app is created
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Beeleva is online.")
    yield

# app is created ONCE here
app = FastAPI(
    title="Beeleva 0.1",
    description="AI-powered business operator for small businesses",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("frontend/index.html")

@app.get("/")
async def root():
    return {"status": "Beeleva 0.1 is online", "ready": True}

@app.post("/inquiry", response_model=InquiryResponse)
async def handle_inquiry(request: InquiryRequest):
    try:
        existing_memory = get_customer_memory(request.email)
        is_returning = existing_memory is not None

        ai_response = process_inquiry(
            email=request.email,
            name=request.name,
            message=request.message
        )

        log_inquiry(
            customer_email=request.email,
            message=request.message,
            intent="inquiry",
            response=ai_response
        )

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

@app.get("/inquiries")
async def get_inquiries():
    return get_all_inquiries()

@app.get("/memory/{email}")
async def get_memory(email: str):
    memory = get_customer_memory(email)
    if not memory:
        return {"message": "No memory found for this customer"}
    return memory