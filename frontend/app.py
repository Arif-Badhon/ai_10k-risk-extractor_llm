import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# Fallback values are critical for Docker resilience
BASE_URL = os.getenv("LLM_BASE_URL", "http://host.docker.internal:12434/v1")
API_KEY = os.getenv("LLM_API_KEY", "unused")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama-3.2-3b")

# Connect to Docker Model Runner
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# --- FUNCTIONS ---

def extract_text_from_pdf(uploaded_file):
    """Extract text from the first 30 pages of a PDF."""
    reader = PdfReader(uploaded_file)
    text = ""
    # Limit pages to prevent token overflow on huge 10-Ks
    max_pages = min(len(reader.pages), 30)
    for i in range(max_pages):
        text += reader.pages[i].extract_text()
    return text

def analyze_risks(text_chunk):
    """Send text to LLM for structured risk extraction."""
    system_prompt = """
    You are a senior financial analyst. Your job is to extract 'Risk Factors' from 10-K reports.
    
    INSTRUCTIONS:
    1. Read the provided text.
    2. Identify the top 5 most critical specific risks (e.g. 'Supply Chain Disruption', 'Regulatory Change').
    3. Score their severity from 1-10.
    4. Categorize them into: 'Market', 'Operational', 'Regulatory', or 'Financial'.
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object with this structure:
    {
        "risks": [
            {
                "risk_title": "Short Title",
                "category": "Category Name",
                "severity_score": 8,
                "description": "One sentence summary of why this is a risk."
            }
        ]
    }
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this 10-K excerpt: \n\n{text_chunk[:12000]}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)})

# --- UI LAYOUT ---

st.set_page_config(page_title="10-K Risk Scanner", layout="wide")

st.title("📉 10-K Risk Factor Scanner")
st.markdown(f"**Connected to:** `{MODEL_NAME}` via Docker Model Runner")

uploaded_file = st.file_uploader("Upload 10-K Report (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Processing PDF..."):
        raw_text = extract_text_from_pdf(uploaded_file)
        st.success(f"Loaded {len(raw_text)} characters from document.")

    if st.button("Analyze Risks", type="primary"):
        with st.spinner("🤖 AI Agent is analyzing risk factors..."):
            json_str = analyze_risks(raw_text)
            
            try:
                data = json.loads(json_str)
                
                if "error" in data:
                    st.error(f"Model Error: {data['error']}")
                elif "risks" in data:
                    risks = data["risks"]
                    df = pd.DataFrame(risks)
                    
                    # Top level metrics
                    col1, col2, col3 = st.columns(3)
                    avg_severity = df["severity_score"].mean()
                    top_risk = df.loc[df["severity_score"].idxmax()]["risk_title"]
                    
                    col1.metric("Total Risks Found", len(df))
                    col2.metric("Avg Severity Score", f"{avg_severity:.1f}/10")
                    col3.metric("Critical Risk", top_risk)
                    
                    st.divider()
                    
                    # Visuals
                    chart_col, table_col = st.columns([1, 2])
                    
                    with chart_col:
                        st.subheader("Risk Distribution")
                        fig = px.pie(df, names='category', values='severity_score', hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    with table_col:
                        st.subheader("Detailed Findings")
                        st.dataframe(
                            df,
                            column_config={
                                "severity_score": st.column_config.ProgressColumn(
                                    "Severity", min_value=0, max_value=10, format="%d"
                                ),
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                else:
                    st.warning("No risks found. Try a different PDF section.")
                    
            except json.JSONDecodeError:
                st.error("Failed to parse model response. Please try again.")
                st.code(json_str)
