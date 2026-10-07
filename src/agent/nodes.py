import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from src.agent.state import InvoiceProcessingState
from src.guardrails.pii_scrubber import PIIScrubber

# Pydantic models for structured output extraction
class InvoiceExtraction(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    amount: float = Field(description="Total amount of the invoice")
    notes: str = Field(description="Any notes or descriptions on the invoice")

class FraudRiskAnalysis(BaseModel):
    risk_score: float = Field(description="Score between 0.0 (safe) and 1.0 (high risk)")
    reasoning: str = Field(description="Reasoning for the risk score")

class ApprovalDecision(BaseModel):
    is_approved: bool = Field(description="True if invoice should be paid, False otherwise")
    reasoning: str = Field(description="Reasoning for the approval or rejection")

# Nodes
def scrub_pii(state: InvoiceProcessingState):
    """Scrub PII from the raw invoice text using Presidio."""
    scrubber = PIIScrubber()
    raw_text = state.get("raw_invoice_text", "")
    scrubbed_text = scrubber.scrub(raw_text)
    return {"scrubbed_invoice_text": scrubbed_text}

def extract_invoice_data(state: InvoiceProcessingState):
    """Extract structured data from the scrubbed invoice."""
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    structured_llm = llm.with_structured_output(InvoiceExtraction)
    
    scrubbed_text = state.get("scrubbed_invoice_text", "")
    
    prompt = f"Extract the invoice details from the following text:\n\n{scrubbed_text}"
    
    result = structured_llm.invoke(prompt)
    return {"extracted_data": result.model_dump()}

def analyze_fraud_risk(state: InvoiceProcessingState):
    """Analyze the extracted data for potential fraud risk."""
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    structured_llm = llm.with_structured_output(FraudRiskAnalysis)
    
    extracted_data = state.get("extracted_data", {})
    
    prompt = f"""
    Analyze the following invoice data for fraud risk.
    Vendor: {extracted_data.get('vendor_name')}
    Amount: ${extracted_data.get('amount')}
    Notes: {extracted_data.get('notes')}
    
    Rules for fraud:
    - Amounts over $50,000 are high risk.
    - Suspicious notes like 'urgent wire transfer' or 'offshore account' increase risk.
    - Unknown or heavily redacted vendors (like <PERSON> or <ORG>) might be riskier if amount is high.
    
    Provide a risk score (0.0 to 1.0) and reasoning.
    """
    
    result = structured_llm.invoke(prompt)
    return {
        "fraud_risk_score": result.risk_score,
        "fraud_risk_reasoning": result.reasoning
    }

def make_approval_decision(state: InvoiceProcessingState):
    """Make a final approval decision based on fraud risk."""
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
    structured_llm = llm.with_structured_output(ApprovalDecision)
    
    fraud_score = state.get("fraud_risk_score", 0.0)
    fraud_reasoning = state.get("fraud_risk_reasoning", "")
    amount = state.get("extracted_data", {}).get("amount", 0.0)
    
    prompt = f"""
    You are an automated B2B Invoice Approver.
    The invoice is for ${amount}.
    The fraud risk score is {fraud_score} (0.0 to 1.0).
    Fraud risk reasoning: {fraud_reasoning}
    
    Policy:
    - Automatically approve if fraud risk <= 0.3 and amount < $10,000.
    - Reject if fraud risk > 0.7.
    - Otherwise, route for manual review (which means reject for automated processing).
    
    Make your decision and provide reasoning.
    """
    
    result = structured_llm.invoke(prompt)
    return {
        "is_approved": result.is_approved,
        "decision_reasoning": result.reasoning
    }
