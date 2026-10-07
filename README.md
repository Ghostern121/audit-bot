---
title: Governance-First Audit Bot
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: streamlit
app_file: app.py
pinned: false
---
# The Audit Bot: Governance-First MLOps System

This project is a multi-agent system designed with strict AI Governance and Guardrails. It acts as an automated B2B Invoice Approver & Fraud Risk Scorer.

## Core Features
- **PII & Safety Guardrails**: Uses Microsoft Presidio to dynamically scrub sensitive information (like SSNs, emails) before the data reaches the LLM.
- **Evaluation-as-a-Judge**: An automated pipeline that programmatically scores the agent's performance using an LLM-as-a-judge node to ensure adherence to company policy.
- **Audit Logging**: Integrates with Langfuse to trace every decision and API call made by the agent. Every run generates a unique tracking ID mapped to the immutable trace on Langfuse for compliance audits.
- **Agentic Workflow**: Uses LangGraph to orchestrate a stateful, multi-step reasoning process (Scrub -> Extract -> Analyze -> Decide -> Evaluate).

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure API Keys**
   - Add your `GROQ_API_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` in the Streamlit cloud settings.

3. **Run the Bot Locally**
   ```bash
   streamlit run app.py
   ```

## Architecture
1. **PII Scrubber Node**: Detects and anonymizes PII using Presidio.
2. **Extraction Node**: Uses Groq to extract structured data from the clean text.
3. **Fraud Risk Node**: Analyzes the structured data against fraud rules.
4. **Approval Node**: Makes the final decision based on company policy.
5. **Judge Node**: Evaluates the agent's decision for safety and correctness.
