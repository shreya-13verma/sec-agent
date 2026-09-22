"""Chat and SSE Streaming Endpoints."""
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.chat import ChatSession, ChatMessage
from backend.app.models.report import RemediationApproval
from backend.app.schemas.chat import ChatMessageCreate, ChatSessionResponse, ChatMessageResponse
from backend.app.agent.graph import compliance_agent

router = APIRouter()

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_chat_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(desc(ChatSession.updated_at)))
    sessions = result.scalars().all()
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return messages

@router.post("/message")
async def send_chat_message(request: ChatMessageCreate, db: AsyncSession = Depends(get_db)):
    # 1. Resolve or create chat session
    session_id = request.session_id
    if not session_id:
        new_session = ChatSession(title=request.message[:40] + ("..." if len(request.message) > 40 else ""))
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        session_id = new_session.id
    else:
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session_obj = result.scalars().first()
        if not session_obj:
            new_session = ChatSession(id=session_id, title=request.message[:40])
            db.add(new_session)
            await db.commit()

    # 2. Save user message to database
    user_msg = ChatMessage(
        session_id=session_id,
        sender="user",
        content=request.message,
        thought_log=""
    )
    db.add(user_msg)
    await db.commit()

    # 3. Stream agent execution steps and tokens via SSE generator
    async def event_generator():
        # Yield session ID event first
        yield {
            "event": "session_id",
            "data": json.dumps({"session_id": session_id})
        }

        # Initialize LangGraph state
        initial_state = {
            "session_id": session_id,
            "user_query": request.message,
            "intent": None,
            "thought_log": [],
            "tool_calls": [],
            "approval_required": False,
            "approval_token": None,
            "remediation_plan": None,
            "final_response": "",
            "status": "PROCESSING"
        }

        final_state = initial_state
        try:
            # Stream execution
            final_state = await asyncio.to_thread(compliance_agent.invoke, initial_state)
            
            # Emit thoughts
            for thought in final_state.get("thought_log", []):
                yield {
                    "event": "thought",
                    "data": json.dumps({"thought": thought})
                }
                await asyncio.sleep(0.05)

            # Emit tool calls
            for tool_call in final_state.get("tool_calls", []):
                yield {
                    "event": "tool_call",
                    "data": json.dumps({"tool": tool_call.get("tool"), "status": "executed"})
                }
                await asyncio.sleep(0.05)

            # If approval required, persist approval token in DB
            if final_state.get("approval_required") and final_state.get("approval_token"):
                plan = final_state.get("remediation_plan", {})
                approval_record = RemediationApproval(
                    approval_token=final_state["approval_token"],
                    session_id=session_id,
                    server_id=plan.get("server_id", 1001),
                    proposed_errata_ids=",".join(map(str, plan.get("errata_ids", []))),
                    status="pending"
                )
                db.add(approval_record)
                await db.commit()

                yield {
                    "event": "approval_required",
                    "data": json.dumps({
                        "approval_token": final_state["approval_token"],
                        "plan": plan
                    })
                }

            # Stream message chunks for typing effect
            full_text = final_state.get("final_response", "")
            words = full_text.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + " "
                yield {
                    "event": "token",
                    "data": json.dumps({"token": chunk})
                }
                await asyncio.sleep(0.02)

            # Save assistant message to DB
            bot_msg = ChatMessage(
                session_id=session_id,
                sender="agent",
                content=full_text,
                thought_log="\n".join(final_state.get("thought_log", []))
            )
            db.add(bot_msg)
            await db.commit()

            yield {
                "event": "done",
                "data": json.dumps({"status": "completed", "session_id": session_id})
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())
