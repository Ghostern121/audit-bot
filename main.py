import os
import json
import uuid
import sys
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler
from src.agent.graph import build_graph

# Load environment variables
load_dotenv()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("--- The Audit Bot: Governance-First MLOps System ---")
    
    # Initialize Langfuse Callback Handler for tracing and audit logging
    langfuse_handler = CallbackHandler()
    
    # Check if keys are actually set
    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("LANGFUSE_PUBLIC_KEY") or not os.environ.get("LANGFUSE_SECRET_KEY"):
        print("WARNING: API keys are not fully set in .env file. The application may fail.")
    
    app = build_graph()
    
    # Load sample invoice
    sample_invoice = """
    Invoice #12345
    From: Acme Corp (acme@example.com)
    To: Globex Inc (globex@example.com)
    Amount: $10,000.00
    Account Number: 1234-5678-9012-3456
    Social Security: 000-00-0000
    Notes: Please process this invoice immediately. Send funds to offshore account X.
    """
    
    print("\n[Input] Processing new invoice...")
    
    # Initial state
    initial_state = {
        "raw_invoice_text": sample_invoice
    }
    
    # Config with Langfuse for Audit Logging
    # We generate a unique run ID for audit tracking
    audit_tracking_id = str(uuid.uuid4())
    config = {
        "configurable": {"thread_id": audit_tracking_id},
        "callbacks": [langfuse_handler],
        "run_name": "AuditBot_Invoice_Approval"
    }
    
    print(f"[Audit] Tracking ID generated: {audit_tracking_id}")
    
    # Run the graph
    result_state = None
    try:
        # We invoke the graph. The callbacks will automatically stream traces to Langfuse.
        result_state = app.invoke(initial_state, config=config)
    except Exception as e:
        print(f"Error during execution: {e}")
        return

    # Print results
    print("\n--- Results ---")
    print(f"Scrubbed Invoice Text:\n{result_state.get('scrubbed_invoice_text')}")
    print("\nExtracted Data:")
    print(json.dumps(result_state.get("extracted_data", {}), indent=2))
    
    print("\nFraud Risk:")
    print(f"Score: {result_state.get('fraud_risk_score')}")
    print(f"Reasoning: {result_state.get('fraud_risk_reasoning')}")
    
    print("\nAgent Decision:")
    print(f"Approved: {result_state.get('is_approved')}")
    print(f"Reasoning: {result_state.get('decision_reasoning')}")
    
    print("\nLLM-as-a-Judge Evaluation:")
    print(f"Score: {result_state.get('evaluation_score')}")
    print(f"Reasoning: {result_state.get('evaluation_reasoning')}")
    
    print("\n--- Audit Trail ---")
    print(f"All actions, including PII scrubbing, extraction, and evaluation have been logged to Langfuse.")
    print(f"Trace ID for compliance audit: {audit_tracking_id}")

if __name__ == "__main__":
    main()
