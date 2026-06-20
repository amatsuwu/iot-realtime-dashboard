import streamlit as st

def init_session_state():
    """
    初始化 Streamlit 的 Session State。
    確保所有的狀態變數都有預設值，避免 KeyError。
    """
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None

def login(token: str, username: str, role: str):
    """
    登入成功後，將使用者資訊寫入 Session State。
    """
    st.session_state.token = token
    st.session_state.username = username
    st.session_state.role = role

def logout():
    """
    登出時，清空 Session State 中的使用者資訊。
    """
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None

def is_authenticated() -> bool:
    """
    檢查使用者是否已經登入。
    """
    return st.session_state.token is not None
