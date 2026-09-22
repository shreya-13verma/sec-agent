"""API v1 Router aggregation."""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import chat, systems, compliance, approvals, reports

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(systems.router, prefix="/systems", tags=["systems"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
