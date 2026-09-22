"""Stateful LangGraph Agent Workflow for SUSE MLM Security & Compliance."""
from langgraph.graph import StateGraph, END
from backend.app.agent.state import AgentState
from backend.app.agent.nodes import (
    analyze_intent,
    execute_tools,
    plan_remediation,
    synthesize_response
)

def route_intent(state: AgentState) -> str:
    """Route to remediation planner (human-in-the-loop) or read-only tools."""
    if state.get("intent") == "remediation_request":
        return "remediation_planner"
    return "tool_executor"

def build_compliance_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_analyzer", analyze_intent)
    workflow.add_node("tool_executor", execute_tools)
    workflow.add_node("remediation_planner", plan_remediation)
    workflow.add_node("synthesizer", synthesize_response)

    workflow.set_entry_point("intent_analyzer")

    workflow.add_conditional_edges(
        "intent_analyzer",
        route_intent,
        {
            "remediation_planner": "remediation_planner",
            "tool_executor": "tool_executor"
        }
    )

    workflow.add_edge("tool_executor", "synthesizer")
    workflow.add_edge("remediation_planner", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()

compliance_agent = build_compliance_agent()
