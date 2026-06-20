import streamlit as st
from utils.state import init_session_state

st.set_page_config(page_title="Admin", layout="wide")
init_session_state()

if not st.session_state.authenticated:
    st.warning("Please login from the main page.")
    st.stop()

user = st.session_state.user
if user and user.get("role") != "Admin":
    st.error("您沒有權限存取此頁面。")
    st.stop()

st.title("系統管理")
st.write("這是僅限 Admin 存取的區域。")
st.write("### 系統狀態")
st.success("所有服務運行正常")
