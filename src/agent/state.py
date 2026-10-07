from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class InvoiceProcessingState(TypedDict):
    """
    State for the invoice processing agent.
    """
    # Raw input invoice text
    raw_invoice_text: str
    
    # Scrubbed invoice text (PII removed)
    scrubbed_invoice_text: str
    
    # Extracted fields from the invoice
    extracted_data: dict
    
    # Fraud risk analysis
    fraud_risk_score: float
    fraud_risk_reasoning: str
    
    # Final approval decision
    is_approved: bool
    decision_reasoning: str
    
    # Judge Evaluation
    evaluation_score: float
    evaluation_reasoning: str
    
    # Conversation/Message history if needed for the LLM
    messages: Annotated[Sequence[BaseMessage], operator.add]
