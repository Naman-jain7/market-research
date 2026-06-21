import streamlit as st
import os
import requests
from typing import Optional
from ui.auth import require_authentication
from ui.styles import apply_styles, page_header
from src.workflow.state import AppState

# Initialize an empty default app state just for default values
app_state = AppState(user_id=0)

API_URL = "http://localhost:8000/api/v1/research"

# Ensure user is logged in
require_authentication()

# Apply standard style guidelines
apply_styles()

page_header(
    title="Market Research Assistant",
    subtitle="Submit your product idea to run real-time agent analysis on market size, competitors, monetization, and strategy.",
    eyebrow="Research"
)

# Initialize session state for persisting agent outputs and scores
def init_session_state():
    keys = {
        "market_research_output": app_state.market_research.text or None,
        "competitive_intelligence_output": app_state.competitive_intelligence.text or None,
        "customer_insights_output": app_state.customer_insights.text or None,
        "product_strategy_output": app_state.product_strategy.text or None,
        "business_analyst_output": app_state.business_analyst.text or None,
        "market_research_score": app_state.market_research.score,
        "competitive_intelligence_score": app_state.competitive_intelligence.score,
        "customer_insights_score": app_state.customer_insights.score,
        "product_strategy_score": app_state.product_strategy.score,
        "business_analyst_score": app_state.business_analyst.score,
    }
    for key, val in keys.items():
        if key not in st.session_state or st.session_state[key] is None:
            st.session_state[key] = val

init_session_state()

def escape_markdown(text: str) -> str:
    if not text:
        return ""
    # Escape dollar signs to prevent Streamlit from interpreting them as LaTeX math blocks
    return text.replace("$", r"\$")

# Text area for user inputs
product_idea = st.text_area(
    "Describe your product idea or research topic:",
    placeholder="e.g., An AI-powered tool that summarizes YouTube videos on my channel and posts them to LinkedIn, X, and WhatsApp.",
    height=150
)

# Button to trigger the research flow
if st.button("Run Market Analysis", type="primary", use_container_width=True):
    if not product_idea.strip():
        st.error("Please enter a valid product idea before running the analysis.")
    else:
        # Set loading indicators
        st.session_state.market_research_output = "Preparing agent..."
        st.session_state.competitive_intelligence_output = "Preparing agent..."
        st.session_state.customer_insights_output = "Preparing agent..."
        st.session_state.product_strategy_output = "Preparing agent..."
        st.session_state.business_analyst_output = "Preparing agent..."
        
        st.session_state.market_research_score = None
        st.session_state.competitive_intelligence_score = None
        st.session_state.customer_insights_score = None
        st.session_state.product_strategy_score = None
        st.session_state.business_analyst_score = None

        try:
            inputs = {
                "user_id": st.session_state.user_id,
                "user_input": product_idea,
            }
            
            with st.spinner("Agents are collaborating on your request..."):
                response = requests.post(
                    API_URL,
                    json=inputs,
                    timeout=300
                )
                
                if response.status_code == 200:
                    state_data = response.json()
                    
                    # Store output in session state
                    st.session_state.market_research_output = state_data["market_research"]["text"] or "No output yet"
                    st.session_state.competitive_intelligence_output = state_data["competitive_intelligence"]["text"] or "No output yet"
                    st.session_state.customer_insights_output = state_data["customer_insights"]["text"] or "No output yet"
                    st.session_state.product_strategy_output = state_data["product_strategy"]["text"] or "No output yet"
                    st.session_state.business_analyst_output = state_data["business_analyst"]["text"] or "No output yet"
                    
                    st.session_state.market_research_score = state_data["market_research"]["score"]
                    st.session_state.competitive_intelligence_score = state_data["competitive_intelligence"]["score"]
                    st.session_state.customer_insights_score = state_data["customer_insights"]["score"]
                    st.session_state.product_strategy_score = state_data["product_strategy"]["score"]
                    st.session_state.business_analyst_score = state_data["business_analyst"]["score"]
                    
                    # Ensure the reports directory exists
                    os.makedirs("reports", exist_ok=True)
                    
                    # Save each agent's output to a separate file
                    outputs_to_save = {
                        "reports/market_research.md": state_data["market_research"]["text"],
                        "reports/competitive_intelligence.md": state_data["competitive_intelligence"]["text"],
                        "reports/customer_insights.md": state_data["customer_insights"]["text"],
                        "reports/product_strategy.md": state_data["product_strategy"]["text"],
                        "reports/business_analyst.md": state_data["business_analyst"]["text"],
                    }
                    for path, text in outputs_to_save.items():
                        if text:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(text)
                                
                    st.rerun()
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
            
        except Exception as e:
            st.error(f"An error occurred during agent execution: {e}")

# Dialog to display full output
@st.dialog("Full Output", width="large")
def show_full_output(title: str, text: str):
    st.markdown(f"### {title}")
    st.markdown(text)

# Render agent card component
def render_agent_card(title: str, text: Optional[str], default_status: str, key_suffix: str, download_filename: str):
    with st.container(border=True):
        col_title, col_download = st.columns([2.5, 1])
        with col_title:
            st.markdown(f"#### {title}")
        with col_download:
            if text and text not in ["Preparing agent...", "Waiting for agent to start...", "No output yet"]:
                st.download_button(
                    label="📥 Download",
                    data=text,
                    file_name=download_filename,
                    mime="text/markdown",
                    key=f"dl_{key_suffix}",
                    use_container_width=True
                )
        if not text:
            st.info(default_status)
        elif text == "Preparing agent...":
            st.info(text)
        else:
            char_count = 350
            escaped_text = escape_markdown(text)
            if len(text) > char_count:
                snippet = escaped_text[:char_count] + "..."
                st.markdown(snippet)
                st.button("View Full Output", key=f"btn_full_{key_suffix}", use_container_width=True, on_click=show_full_output, args=(title, escaped_text))
            else:
                st.markdown(escaped_text)

# Create sections for displaying agent outputs
st.markdown("---")
st.subheader("Agent Outputs")

col1, col2 = st.columns(2)

with col1:
    render_agent_card(
        "📊 1. Market Research",
        st.session_state.market_research_output,
        "Waiting for agent to start...",
        "mr",
        "market_research.md"
    )
    render_agent_card(
        "👥 3. Customer Insights",
        st.session_state.customer_insights_output,
        "Waiting for agent to start...",
        "ci",
        "customer_insights.md"
    )
    render_agent_card(
        "📈 5. Business Analysis",
        st.session_state.business_analyst_output,
        "Waiting for agent to start...",
        "ba",
        "business_analyst.md"
    )

with col2:
    render_agent_card(
        "🔍 2. Competitive Intelligence",
        st.session_state.competitive_intelligence_output,
        "Waiting for agent to start...",
        "comp",
        "competitive_intelligence.md"
    )
    render_agent_card(
        "🎯 4. Product Strategy",
        st.session_state.product_strategy_output,
        "Waiting for agent to start...",
        "ps",
        "product_strategy.md"
    )

# Show scores from each agent
st.markdown("---")
st.subheader("Agent Scores")
score_cols = st.columns(5)
agent_labels = [
    ("Market Research", st.session_state.market_research_score),
    ("Competitive Intel", st.session_state.competitive_intelligence_score),
    ("Customer Insights", st.session_state.customer_insights_score),
    ("Product Strategy", st.session_state.product_strategy_score),
    ("Business Analyst", st.session_state.business_analyst_score),
]
for col, (label, score) in zip(score_cols, agent_labels):
    with col:
        st.metric(label, f"{score:.1f}" if score is not None else "N/A")

# Check if report was generated and provide a download option
report_path = "reports/report.md"
if os.path.exists(report_path):
    st.divider()
    st.subheader("Generated Report")
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()
        
        st.download_button(
            label="Download Completed Report (.md)",
            data=report_text,
            file_name="market_research_report.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        with st.expander("Preview Report"):
            st.markdown(escape_markdown(report_text))
            
    except Exception as e:
        st.warning(f"Could not load the generated report file: {e}")
