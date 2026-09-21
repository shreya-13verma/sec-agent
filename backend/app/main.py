import os
import sys
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add parent directory to sys.path to ensure robust package imports
sys.path.insert(0, "/home/shreya/compliance-agent")

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.utils.seed_data import seed_database
from backend.app.routers import (
    auth, hosts, compliance, agent, remediation, reports, audit_logs
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    # Seed default data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Autonomous security and compliance system for SUSE Multi-Linux Manager (MLM) fleets with agentic reasoning, CIS/HIPAA audits, and controlled remediation.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(hosts.router, prefix=settings.API_V1_STR)
app.include_router(compliance.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)
app.include_router(remediation.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(audit_logs.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "mlm_adapter": "ready",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }
