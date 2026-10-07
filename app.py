import streamlit as st
import os
import uuid
import pandas as pd
import PyPDF2
import time
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler
from src.agent.graph import build_graph
import sys

# Load env variables
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

st.set_page_config(page_title="Audit Bot: AI Governance", layout="wide", initial_sidebar_state="expanded")

# --- Session State Initialization ---
if "stage" not in st.session_state:
    st.session_state.stage = "start"
if "show_arch" not in st.session_state:
    st.session_state.show_arch = False
if "motivate_clicked" not in st.session_state:
    st.session_state.motivate_clicked = False

# --- Helper Functions ---
def set_bg_video(video_filename):
    """Sets a fixed background video using static serving."""
    video_url = f"/app/static/{video_filename}"
    unique_id = video_filename.replace('.', '_')
    st.markdown(f"""
        <style>
        .bg-vid {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -100;
            object-fit: cover;
            opacity: 0.8;
        }}
        /* Make Streamlit background transparent */
        .stApp {{
            background-color: transparent !important;
        }}
        .stApp > header {{
            background-color: transparent !important;
        }}
        /* Add semi-transparent dark background to main content blocks for readability */
        .block-container {{
            background-color: rgba(14, 17, 23, 0.85) !important;
            padding: 2rem !important;
            border-radius: 15px;
            margin-top: 2rem;
        }}
        </style>
        <div id="wrapper_{unique_id}">
            <video autoplay loop muted playsinline class="bg-vid" id="{unique_id}" src="{video_url}"></video>
        </div>
    """, unsafe_allow_html=True)

def process_invoice(text, run_name):
    """Helper function to run the LangGraph pipeline on a piece of text."""
    audit_tracking_id = str(uuid.uuid4())
    langfuse_handler = CallbackHandler()
    app = build_graph()
    
    config = {
        "configurable": {"thread_id": audit_tracking_id},
        "callbacks": [langfuse_handler],
        "run_name": run_name
    }
    initial_state = {"raw_invoice_text": text}
    result = app.invoke(initial_state, config=config)
    result['audit_tracking_id'] = audit_tracking_id
    return result

# --- Page Routing ---

if st.session_state.stage == "start":
    # 1. START PAGE
    set_bg_video("start_scene.mp4")
    
    st.title("🛡️ Governance-First 'Agentic' MLOps System")
    st.markdown("### The Audit Bot: Automated B2B Invoice Approver & Fraud Risk Scorer")
    st.info("Welcome! This project demonstrates a multi-agent AI system with strict governance guardrails. "
            "It scrubs PII dynamically using Microsoft Presidio, extracts structured data, scores fraud risk, "
            "and finally audits its own decision using an LLM-as-a-judge.")
    
    # Push button down slightly
    st.write("")
    st.write("")
    if st.button("🚀 START PLATFORM", use_container_width=True, type="primary"):
        st.session_state.stage = "loading"
        st.rerun()

elif st.session_state.stage == "loading":
    # 2. LOADING PAGE
    set_bg_video("loading_delay.mp4")
    st.title("Loading Secure Environment...")
    st.warning("Initializing Guardrails, loading LangGraph workflows, and establishing secure Langfuse audit tunnels...")
    
    # Add a visual progress bar that completes in 5 seconds
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.05)
        progress.progress(i + 1)
        
    st.session_state.stage = "main"
    st.rerun()

elif st.session_state.stage == "main":
    # 3. MAIN APP PAGE
    set_bg_video("working_scene.mp4")
    
    st.title("🛡️ The Audit Bot Dashboard")
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("Controls & Metadata")
        
        # Architecture Details Toggle
        if st.button("Show Architecture"):
            st.session_state.show_arch = not st.session_state.show_arch
            
        if st.session_state.show_arch:
            st.markdown("""
            **System Components:**
            - **PII Guardrails:** Microsoft Presidio
            - **Multi-Agent Flow:** LangGraph
            - **LLM Judge:** Groq `openai/gpt-oss-120b`
            - **Audit Log:** Langfuse
            """)
            
        st.divider()
        
        # Motivate Button
        if st.button("Keep Motivated 💪"):
            st.session_state.motivate_clicked = not st.session_state.motivate_clicked
            
        if st.session_state.motivate_clicked:
            st.video("static/Motivate.mp4", autoplay=True)
            
        st.divider()
        
        # Placeholder for dynamic mini-screen video during processing
        mini_video_placeholder = st.empty()
        
    # --- Main Content ---
    st.subheader("📄 Batch PDF Upload")
    st.write("Upload single or multiple PDFs. The system will extract text (treating each page as an invoice example) and process them all.")
    
    uploaded_files = st.file_uploader("Upload Invoice PDFs", type=["pdf"], accept_multiple_files=True)
    
    # Hidden placeholder for background audio
    audio_placeholder = st.empty()
    
    if st.button("Process PDFs", type="primary") and uploaded_files:
        # Start "cash loop" audio in the background
        audio_placeholder.markdown("""
            <audio autoplay loop src="/app/static/cash_loop.mp3" style="display:none;"></audio>
        """, unsafe_allow_html=True)
        
        # Start "Motivate" video on mini screen (muted) using native st.video
        with mini_video_placeholder.container():
            st.markdown("<p><b>Processing Mode Active ⚙️</b></p>", unsafe_allow_html=True)
            st.video("static/Motivate.mp4", autoplay=True, muted=True, loop=True)
        
        invoices_to_process = []
        
        # Extract text from PDFs
        with st.spinner("Extracting text from PDFs..."):
            for file in uploaded_files:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page_text = pdf_reader.pages[page_num].extract_text()
                        if page_text and len(page_text.strip()) > 10:
                            invoices_to_process.append({
                                "source": f"{file.name} (Page {page_num + 1})",
                                "text": page_text
                            })
                except Exception as e:
                    st.error(f"Failed to read {file.name}: {e}")
        
        if not invoices_to_process:
            st.warning("No valid text found in the uploaded PDFs.")
            audio_placeholder.empty()
            mini_video_placeholder.empty()
        else:
            st.info(f"Extracted {len(invoices_to_process)} invoice(s). Processing through Governance Pipeline...")
            
            results_data = []
            progress_bar = st.progress(0)
            
            # Process each invoice
            for idx, inv in enumerate(invoices_to_process):
                try:
                    res = process_invoice(inv["text"], f"AuditBot_Batch_{idx}")
                    
                    extracted = res.get("extracted_data", {})
                    vendor = extracted.get("vendor_name", "Unknown")
                    amount = extracted.get("amount", 0.0)
                    score = res.get("fraud_risk_score", 0.0)
                    is_approved = res.get("is_approved", False)
                    status = "Approved" if is_approved else "Rejected / Manual Review"
                    eval_score = res.get("evaluation_score", 1.0)
                    
                    results_data.append({
                        "Source": inv["source"],
                        "Vendor": vendor,
                        "Amount ($)": amount,
                        "Fraud Risk": score,
                        "Status": status,
                        "Judge Score": eval_score,
                        "Tracking ID": res['audit_tracking_id']
                    })
                except Exception as e:
                    st.error(f"Error processing {inv['source']}: {e}")
                
                progress_bar.progress((idx + 1) / len(invoices_to_process))
                
            st.success("Batch Processing Complete!")
            
            # Stop the loop audio and mini video
            audio_placeholder.empty()
            mini_video_placeholder.empty()
            
            # Play "cash rec" audio once
            st.markdown("""
                <audio autoplay src="/app/static/cash_rec.mp3" style="display:none;"></audio>
            """, unsafe_allow_html=True)
            
            # Display interactive dataframe
            if results_data:
                df = pd.DataFrame(results_data)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Processed", len(df))
                col2.metric("Approved", len(df[df["Status"] == "Approved"]))
                col3.metric("High Risk (>0.5)", len(df[df["Fraud Risk"] > 0.5]))
                col4.metric("Total Amount", f"${df['Amount ($)'].sum():,.2f}")
                
                st.subheader("Invoice Results Dashboard")
                
                st.dataframe(
                    df,
                    column_config={
                        "Fraud Risk": st.column_config.ProgressColumn(
                            "Fraud Risk",
                            help="Fraud Risk Score (0 to 1)",
                            format="%f",
                            min_value=0,
                            max_value=1,
                        ),
                        "Amount ($)": st.column_config.NumberColumn(
                            "Amount ($)",
                            format="$%.2f"
                        ),
                        "Judge Score": st.column_config.NumberColumn(
                            "Judge Score",
                            format="%.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info(f"[View All Immutable Traces on Langfuse Dashboard]({os.environ.get('LANGFUSE_BASE_URL', 'https://us.cloud.langfuse.com')})")
