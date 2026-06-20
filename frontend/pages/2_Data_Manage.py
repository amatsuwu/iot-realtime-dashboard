import streamlit as st
import pandas as pd
from utils.state import init_session_state
from utils.api_client import fetch_data

st.set_page_config(page_title="Data Manage", layout="wide")
init_session_state()

if not st.session_state.authenticated:
    st.warning("Please login from the main page.")
    st.stop()

st.title("資料管理")

st.subheader("歷史資料查詢")
data = fetch_data()
if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.info("No data available.")

st.subheader("匯入資料")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
if uploaded_file is not None:
    st.success("File uploaded successfully! (Import logic to be implemented)")
