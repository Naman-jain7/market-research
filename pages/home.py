import streamlit as st
from ui.auth import is_authenticated
from ui.styles import apply_styles, page_header, feature_card

apply_styles()

page_header("Market Research AI Hub", "Empowering you with AI-driven market analysis, competitor scans, and product strategy.", "Home")

col1, col2 = st.columns(2)

with col1:
    feature_card(
        "Deep Market Sizing",
        "Estimate TAM, SAM, and SOM using automated research agents that fetch real-world data and analyze industry trends."
    )

with col2:
    feature_card(
        "Competitive Intelligence",
        "Scan the landscape to identify competitors, analyze their positioning, pricing, and find strategic gaps for your product."
    )

st.divider()

if is_authenticated():
    st.success("You are signed in! Start your research now.")
    if st.button("Go to Research Assistant", type="primary", use_container_width=True):
        st.switch_page("pages/research.py")
else:
    st.info("Sign in to get started with the AI market research agents.")
    col_login, col_signup = st.columns(2)
    with col_login:
        if st.button("Sign In", use_container_width=True):
            st.switch_page("pages/login.py")
    with col_signup:
        if st.button("Create Account", type="primary", use_container_width=True):
            st.switch_page("pages/signup.py")
