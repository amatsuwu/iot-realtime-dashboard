import streamlit as st
from utils.api_client import login
from utils.state import init_session_state

def login_form():
    st.subheader("Login to the System")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            result = login(username, password)
            if result:
                st.session_state.authenticated = True
                st.session_state.token = result["access_token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
