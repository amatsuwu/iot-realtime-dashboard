import asyncio
import websockets
import json

async def test_websocket():
    # 這是您剛剛在 routers/monitor.py 建立的連線閘口網址
    uri = "ws://127.0.0.1:8000/api/v1/monitor/ws"
    
    print(f"嘗試連線至 WebSocket 伺服器: {uri}")
    try:
        # 建立連線
        async with websockets.connect(uri) as websocket:
            print("✅ 成功連線！正在等待伺服器推播即時資料...\n")
            print("-" * 50)
            
            # 無窮迴圈：不斷接收伺服器推過來的訊息
            while True:
                response = await websocket.recv()
                
                # 將接收到的 JSON 字串轉成 Python 字典，方便排版印出
                data = json.loads(response)
                
                # 判斷是否為異常告警並加上醒目符號
                alert_symbol = "🚨 [告警]" if data.get("is_alert") else "✅ [正常]"
                
                print(f"{alert_symbol} 時間: {data['timestamp']}")
                print(f"    分類: {data['category']} | 數值: {data['value']}")
                print("-" * 50)
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ 連線已關閉")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    # 啟動非同步事件迴圈
    asyncio.run(test_websocket())
