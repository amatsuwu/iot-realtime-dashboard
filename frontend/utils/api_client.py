import os
import requests
import streamlit as st

# 從環境變數讀取後端網址，預設為 localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
BASE_URL = f"{BACKEND_URL}/api/v1"

def get_headers():
    """
    自動從 Session State 中取出 Token，並組合成 HTTP Headers。
    """
    headers = {}
    if "token" in st.session_state and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def get(endpoint: str, params=None):
    """封裝 GET 請求"""
    url = f"{BASE_URL}{endpoint}"
    return requests.get(url, headers=get_headers(), params=params)

def post(endpoint: str, json_data=None, data=None, files=None):
    """封裝 POST 請求"""
    url = f"{BASE_URL}{endpoint}"
    return requests.post(url, headers=get_headers(), json=json_data, data=data, files=files)

def delete(endpoint: str):
    """封裝 DELETE 請求"""
    url = f"{BASE_URL}{endpoint}"
    return requests.delete(url, headers=get_headers())
