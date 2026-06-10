from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.routers import surveys, questions, responses, certificates
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Sky Survey API",
    description="Survey Platform REST API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs("app/uploads/certificates", exist_ok=True)

# Include routers
app.include_router(surveys.router, prefix="/api", tags=["Surveys"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])
app.include_router(responses.router, prefix="/api", tags=["Responses"])
app.include_router(certificates.router, prefix="/api", tags=["Certificates"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Sky Survey API", "docs": "/docs", "redoc": "/redoc"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}