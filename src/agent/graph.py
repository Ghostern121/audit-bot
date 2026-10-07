from langgraph.graph import StateGraph, END
from src.agent.state import InvoiceProcessingState
from src.agent.nodes import scrub_pii, extract_invoice_data, analyze_fraud_risk, make_approval_decision
from src.evaluation.judge import evaluate_agent_decision

def build_graph():
    """Builds and compiles the LangGraph for the invoice processing agent."""
    workflow = StateGraph(InvoiceProcessingState)
    
    # Add nodes
    workflow.add_node("scrub_pii", scrub_pii)
    workflow.add_node("extract_data", extract_invoice_data)
    workflow.add_node("analyze_risk", analyze_fraud_risk)
    workflow.add_node("make_decision", make_approval_decision)
    workflow.add_node("evaluate_decision", evaluate_agent_decision)
    
    # Define edges
    workflow.set_entry_point("scrub_pii")
    workflow.add_edge("scrub_pii", "extract_data")
    workflow.add_edge("extract_data", "analyze_risk")
    workflow.add_edge("analyze_risk", "make_decision")
    workflow.add_edge("make_decision", "evaluate_decision")
    workflow.add_edge("evaluate_decision", END)
    
    # Compile
    app = workflow.compile()
    return app
