import streamlit as st

from ui import api_client
from ui.styles import page_header


page_header("Create your account", "Start chatting with your documents today.", "Account")

left, form_column, right = st.columns([1, 1.5, 1])
with form_column:
    with st.form("signup_form"):
        full_name = st.text_input("Full name", placeholder="John Doe")
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", help="Use at least 8 characters.")
        confirm_password = st.text_input("Confirm password", type="password")
        age_input = st.text_input("Age (optional)", placeholder="e.g., 30")
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

    if submitted:
        if not full_name.strip() or not email.strip():
            st.error("Full name and email are required.")
        elif len(full_name.strip()) > 100:
            st.error("Full name must be 100 characters or fewer.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # parse optional age
            age_val = None
            if age_input and age_input.strip():
                try:
                    age_val = int(age_input)
                    if age_val < 0 or age_val > 150:
                        st.error("Age must be between 0 and 150.")
                        age_val = None
                except ValueError:
                    st.error("Age must be a whole number.")
                    age_val = None
            try:
                api_client.signup(full_name.strip(), email.strip(), password, age_val)
                st.success("Account created successfully! Please login.")
                st.switch_page("pages/login.py")
            except Exception as e:
                st.error(f"Could not connect to server: {e}")

    st.divider()
    st.markdown("Already have an account?")
    if st.button("Back to Login", use_container_width=True):
        st.switch_page("pages/login.py")
