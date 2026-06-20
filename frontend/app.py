import streamlit as st
from utils.state import init_session_state, logout
from components.forms import login_form
from utils.api_client import get_me

st.set_page_config(page_title="Monitor Dashboard", layout="wide")

init_session_state()

if not st.session_state.authenticated:
    st.title("即時資料分析與監控系統")
    login_form()
else:
    # 嘗試取得使用者資訊
    if not st.session_state.user:
        user_info = get_me()
        if user_info:
            st.session_state.user = user_info
        else:
            logout()
            
    st.sidebar.title(f"Welcome, {st.session_state.user.get('username')}")
    st.sidebar.write(f"Role: {st.session_state.user.get('role')}")
    
    if st.sidebar.button("Logout"):
        logout()
        
    st.write("### 請從左側選單選擇頁面")
