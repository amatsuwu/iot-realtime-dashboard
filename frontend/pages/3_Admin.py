import streamlit as st
from frontend.utils import state

if not state.is_authenticated():
    st.error("您尚未登入或連線已逾時，請回到首頁重新登入。")
    st.stop()

# 嚴格的越權防護 (RBAC)
if st.session_state.role != "Admin":
    st.error("越權存取！您沒有權限查看此頁面。")
    st.stop()

st.title("⚙️ 管理員後台")
st.write("這裡是階段五，專屬於 Admin 的系統管理區塊。")
