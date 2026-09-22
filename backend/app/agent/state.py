"""LangGraph Agent State Definition."""
from typing import List, Dict, Any, Optional, TypedDict

class AgentState(TypedDict):
    session_id: str
    user_query: str
    intent: Optional[str]
    thought_log: List[str]
    tool_calls: List[Dict[str, Any]]
    approval_required: bool
    approval_token: Optional[str]
    remediation_plan: Optional[Dict[str, Any]]
    final_response: str
    status: str
