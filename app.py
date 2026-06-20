import streamlit as st
import time
from frontend.utils import state, api_client

# 設定網頁基本設定 (需放在最上方)
st.set_page_config(page_title="即時資料分析與監控系統", layout="wide", page_icon="📡")

# 1. 初始化 Session State
state.init_session_state()

# 2. 定義登入與註冊介面
def login_page():
    st.title("🔐 即時資料分析與監控系統")
    st.write("請先登入或註冊以繼續使用。")
    
    # 使用 Tabs 切換登入與註冊
    tab1, tab2 = st.tabs(["登入", "註冊"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("帳號")
            password = st.text_input("密碼", type="password")
            submitted = st.form_submit_button("登入", use_container_width=True)
            
            if submitted:
                # 呼叫 FastAPI 登入 API (注意：OAuth2 需要使用 data 而非 json_data)
                data = {"username": username, "password": password}
                response = api_client.post("/auth/login", data=data)
                
                if response.status_code == 200:
                    res_data = response.json()
                    # 寫入 Session State
                    state.login(
                        token=res_data["access_token"],
                        username=res_data["user"]["username"],
                        role=res_data["user"]["role"]
                    )
                    st.success("登入成功！準備載入系統...")
                    time.sleep(0.5)
                    st.rerun() # 重新刷新畫面，進入系統
                else:
                    st.error("登入失敗：帳號或密碼錯誤")
                    
    with tab2:
        with st.form("register_form"):
            reg_username = st.text_input("設定帳號")
            reg_password = st.text_input("設定密碼", type="password")
            reg_role = st.selectbox("選擇角色", ["Viewer", "User", "Admin"])
            reg_submitted = st.form_submit_button("註冊", use_container_width=True)
            
            if reg_submitted:
                data = {
                    "username": reg_username,
                    "password": reg_password,
                    "role": reg_role
                }
                # 註冊 API 使用 JSON 格式
                response = api_client.post("/auth/register", json_data=data)
                
                if response.status_code == 201:
                    st.success("註冊成功！請切換到「登入」頁籤進行登入。")
                else:
                    st.error(f"註冊失敗：{response.text}")

# 3. 系統主邏輯
def main():
    if not state.is_authenticated():
        # 如果未登入，強制顯示登入畫面，且完全不掛載側邊欄與其他頁面
        login_page()
    else:
        # 已登入，設定側邊欄顯示使用者資訊與登出按鈕
        with st.sidebar:
            st.title("控制面板")
            st.info(f"👤 **{st.session_state.username}**\\n🏷️ 角色: {st.session_state.role}")
            if st.button("🚪 登出系統", use_container_width=True):
                state.logout()
                st.rerun()
                
        # 【動態路由與權限控制】
        # 利用 Streamlit 最新的 st.navigation API 來控制可見頁面
        pages = {
            "核心功能": [
                st.Page("frontend/pages/1_Dashboard.py", title="即時監控儀表板", icon="📈", default=True),
                st.Page("frontend/pages/2_DataManage.py", title="資料管理與分析", icon="📁"),
            ]
        }
        
        # 角色權限審查：只有 Admin 才能看到並進入管理後台
        if st.session_state.role == "Admin":
            pages["系統管理"] = [
                st.Page("frontend/pages/3_Admin.py", title="管理員後台", icon="⚙️")
            ]
            
        # 啟動路由導航
        pg = st.navigation(pages)
        pg.run()

if __name__ == "__main__":
    main()
