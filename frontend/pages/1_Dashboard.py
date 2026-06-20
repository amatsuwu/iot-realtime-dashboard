import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
import threading
import time
from frontend.utils import state

if not state.is_authenticated():
    st.error("您尚未登入或連線已逾時，請回到首頁重新登入。")
    st.stop()

st.title("📈 即時監控儀表板")
st.write("這裡是即時 WebSocket 串流資料，正在展現 IoT 設備的最新動態！")

# ==========================================
# 狀態層：初始化記憶體資料表與最新狀態
# ==========================================
if "live_data" not in st.session_state:
    st.session_state.live_data = pd.DataFrame(columns=["timestamp", "Temperature", "Humidity", "System_Load"])

if "latest_alert" not in st.session_state:
    st.session_state.latest_alert = None

if "latest_metrics" not in st.session_state:
    st.session_state.latest_metrics = {"Temperature": 0.0, "Humidity": 0.0, "System_Load": 0.0}

# ==========================================
# 邏輯層：背景執行緒 (Background Thread)
# ==========================================
# 解決「無窮迴圈卡死主執行緒」的地雷
def start_websocket_thread():
    async def listen():
        uri = "ws://127.0.0.1:8000/api/v1/monitor/ws"
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    cat = data["category"]
                    val = data["value"]
                    is_alert = data["is_alert"]
                    # 解決 X 軸失真問題：強制將字串轉型為時間格式
                    timestamp = pd.to_datetime(data["timestamp"])
                    
                    # 1. 更新最新數值字典
                    st.session_state.latest_metrics[cat] = val
                    
                    # 2. 更新告警狀態
                    if is_alert:
                        st.session_state.latest_alert = f"🚨 告警：{cat} 數值飆高至 {val}！發生時間：{data['timestamp']}"
                    else:
                        # 如果收到正常資料，且之前的告警是同一個類別，則消除告警
                        if st.session_state.latest_alert and cat in st.session_state.latest_alert:
                            st.session_state.latest_alert = None
                    
                    # 3. 更新歷史資料表 (供折線圖使用)
                    new_row = {"timestamp": timestamp, cat: val}
                    new_df = pd.DataFrame([new_row])
                    
                    st.session_state.live_data = pd.concat([st.session_state.live_data, new_df], ignore_index=True)
                    if len(st.session_state.live_data) > 50:
                        st.session_state.live_data = st.session_state.live_data.tail(50)
                        
        except Exception as e:
            print(f"WebSocket 背景執行緒發生錯誤: {e}")

    # 因為我們是在新開的 Thread 中執行，必須手動建立事件迴圈
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen())

from streamlit.runtime.scriptrunner import add_script_run_ctx

# 確保這個背景執行緒只會被啟動一次
if "ws_thread" not in st.session_state:
    # daemon=True 確保主程式關閉時，這個背景執行緒也會跟著死掉，不會變成殭屍
    thread = threading.Thread(target=start_websocket_thread, daemon=True)
    
    # 🚨 關鍵修復：將 Streamlit 的 Session Context 綁定到這個背景執行緒
    # 否則背景執行緒去讀寫 st.session_state 會發生 RuntimeError
    add_script_run_ctx(thread)
    
    thread.start()
    st.session_state.ws_thread = thread

# ==========================================
# 視覺層：繪製畫面
# ==========================================
# 1. 警報跑馬燈
if st.session_state.latest_alert:
    st.error(st.session_state.latest_alert)
else:
    st.empty() # 佔位避免畫面跳動

# 2. 關鍵指標面板
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌡️ 溫度 (Temperature)", f"{st.session_state.latest_metrics['Temperature']} °C")
with col2:
    st.metric("💧 濕度 (Humidity)", f"{st.session_state.latest_metrics['Humidity']} %")
with col3:
    st.metric("⚙️ 系統負載 (System Load)", f"{st.session_state.latest_metrics['System_Load']} %")

st.divider()

# 3. 即時趨勢圖
st.subheader("即時趨勢圖 (最近 50 筆)")
chart_df = st.session_state.live_data.copy()

if not chart_df.empty:
    # 解決 X 軸失真問題：確保時間欄位是 Index
    chart_df = chart_df.set_index('timestamp')
    st.line_chart(chart_df)
    
    # [新增] 柱狀圖 (Bar Chart)：顯示三種感測器的最新即時數值對比
    st.divider()
    st.subheader("📊 各項指標最新數值對比 (Bar Chart)")
    # 將 dict 轉成 DataFrame 方便畫圖
    bar_df = pd.DataFrame([st.session_state.latest_metrics]).T
    bar_df.columns = ["數值"]
    st.bar_chart(bar_df)
else:
    st.info("等待 WebSocket 資料載入中...")

# ==========================================
# 自動刷新機制 (Heartbeat)
# ==========================================
# 主執行緒休息 1 秒鐘後，主動發起 st.rerun()。
# 這樣一來，Streamlit 就有空檔去處理側邊欄點擊事件，徹底解決卡死問題！
time.sleep(1)
st.rerun()
