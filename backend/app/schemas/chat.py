"""Chat Schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessageCreate(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender: str
    content: str
    thought_log: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
