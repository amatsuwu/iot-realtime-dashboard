import streamlit as st
import plotly.express as px
import pandas as pd

def render_line_chart(data_df: pd.DataFrame, x_col="timestamp", y_col="value", color_col="category", title="Real-time Data"):
    if data_df.empty:
        st.info("No data available to plot.")
        return
        
    fig = px.line(data_df, x=x_col, y=y_col, color=color_col, title=title, markers=True)
    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(data_df: pd.DataFrame, x_col="category", y_col="value", title="Data by Category"):
    if data_df.empty:
        return
    fig = px.bar(data_df, x=x_col, y=y_col, title=title)
    st.plotly_chart(fig, use_container_width=True)
