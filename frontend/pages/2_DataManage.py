import streamlit as st
import pandas as pd
from frontend.utils import api_client, state

# 1. 權限雙重防護
if not state.is_authenticated():
    st.error("您尚未登入或連線已逾時，請回到首頁重新登入。")
    st.stop()

st.title("📁 歷史資料管理與分析")

# ==========================================
# 資料讀取函數
# ==========================================
def load_data(category_filter=None):
    """呼叫後端 API 取得歷史資料"""
    params = {"limit": 1000} # 簡單起見先撈 1000 筆，實務上可做真分頁
    if category_filter and category_filter != "全部":
        params["category"] = category_filter
        
    response = api_client.get("/data/", params=params)
    if response.status_code == 200:
        return response.json()
    return []

# ==========================================
# 介面切分：管理 與 分析
# ==========================================
tab_manage, tab_analyze = st.tabs(["🗄️ 資料管理 (CRUD)", "📊 趨勢分析"])

# -------------------------
# 頁籤 1: 資料管理
# -------------------------
with tab_manage:
    # --- 頂部篩選器 ---
    col_filter, col_refresh = st.columns([3, 1])
    with col_filter:
        selected_category = st.selectbox("依分類篩選", ["全部", "Temperature", "Humidity", "System_Load"])
    with col_refresh:
        st.write("") # 排版對齊用
        if st.button("🔄 重新載入", use_container_width=True):
            st.rerun()

    # --- 資料表格展示 ---
    raw_data = load_data(selected_category)
    
    if not raw_data:
        st.info("目前沒有符合的資料。")
    else:
        df = pd.DataFrame(raw_data)
        # 整理欄位順序
        df_display = df[["id", "title", "category", "value", "timestamp", "creator_id"]]
        
        # Streamlit 內建強大的 DataFrame 展示
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # --- 刪除資料區塊 ---
        st.subheader("🗑️ 刪除資料")
        st.caption("越權防護測試：您只能刪除您自己上傳的資料（除非您是 Admin）")
        
        del_col1, del_col2 = st.columns([3, 1])
        with del_col1:
            delete_id = st.selectbox("選擇要刪除的資料 ID", df["id"].tolist())
        with del_col2:
            st.write("")
            if st.button("確認刪除", type="primary", use_container_width=True):
                del_res = api_client.delete(f"/data/{delete_id}")
                if del_res.status_code == 204:
                    st.success("刪除成功！")
                    st.rerun()
                else:
                    # 這裡完美體現了後端 RBAC 的防護，把 403 錯誤顯示出來
                    st.error(f"刪除失敗：{del_res.json().get('detail')}")

    # --- 批量匯入 CSV 區塊 ---
    st.divider()
    st.subheader("📤 批量匯入 (CSV)")
    st.caption("請上傳我們剛剛建立的 sample_data_test.csv 來測試。")
    uploaded_file = st.file_uploader("選擇 CSV 檔案", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("開始匯入資料", use_container_width=True):
            # 組合 multipart/form-data 格式送給我們辛苦寫好的 batch-import API
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            import_res = api_client.post("/data/batch-import", files=files)
            
            if import_res.status_code == 201:
                st.success(import_res.json().get("message", "匯入成功！"))
                st.rerun()
            else:
                st.error(f"匯入失敗：{import_res.json().get('detail')}")

# -------------------------
# 頁籤 2: 趨勢分析
# -------------------------
with tab_analyze:
    if not raw_data:
        st.info("請先至資料管理頁面新增資料，才能進行分析。")
    else:
        df_chart = pd.DataFrame(raw_data)
        # 資料預處理：字串轉時間，並依時間排序
        df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"])
        df_chart = df_chart.sort_values("timestamp")
        
        # 讓使用者選擇想看哪一條趨勢線
        analyze_category = st.selectbox("選擇要分析的指標", df_chart["category"].unique(), key="analyze_cat")
        df_filtered = df_chart[df_chart["category"] == analyze_category]
        
        # [新增] 📅 時間範圍查詢
        st.write("### 📅 時間範圍查詢")
        min_date = df_filtered["timestamp"].min().date()
        max_date = df_filtered["timestamp"].max().date()
        date_range = st.date_input("選擇時間範圍", [min_date, max_date], min_value=min_date, max_value=max_date)
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
            df_filtered = df_filtered.loc[mask]
        
        if not df_filtered.empty:
            # [新增] 📊 統計分析面板
            st.write("### 📊 統計分析")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("總計 (Sum)", f"{df_filtered['value'].sum():.2f}")
            m2.metric("平均 (Avg)", f"{df_filtered['value'].mean():.2f}")
            m3.metric("最大值 (Max)", f"{df_filtered['value'].max():.2f}")
            m4.metric("最小值 (Min)", f"{df_filtered['value'].min():.2f}")
            
            st.divider()
            
            # 將時間設為 Index，這樣折線圖的 X 軸才會是時間
            chart_data = df_filtered.set_index("timestamp")["value"]
            
            # 繪製美觀的折線圖
            st.line_chart(chart_data)
            
            # [新增] 📥 實作 Excel 下載按鈕
            import io
            excel_buffer = io.BytesIO()
            df_filtered.to_excel(excel_buffer, index=False, engine='openpyxl')
            
            st.download_button(
                label=f"📥 下載 {analyze_category} 分析報告 (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"analytics_report_{analyze_category}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("該區間段內目前無資料可供分析。")
