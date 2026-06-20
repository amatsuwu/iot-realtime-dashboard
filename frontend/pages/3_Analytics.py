import streamlit as st
import pandas as pd
from utils.state import init_session_state
from utils.api_client import fetch_data
from components.charts import render_bar_chart

st.set_page_config(page_title="Analytics", layout="wide")
init_session_state()

if not st.session_state.authenticated:
    st.warning("Please login from the main page.")
    st.stop()

st.title("資料分析")

data = fetch_data()
if data:
    df = pd.DataFrame(data)
    st.write("### 基礎統計")
    st.write(df.describe())
    
    st.write("### 分類統計")
    if 'category' in df.columns:
        cat_df = df.groupby('category').agg({'value': 'mean'}).reset_index()
        render_bar_chart(cat_df, x_col="category", y_col="value", title="平均數值 (依分類)")
else:
    st.info("No data available for analysis.")
