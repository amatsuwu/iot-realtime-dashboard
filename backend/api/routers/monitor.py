from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.websocket import manager

router = APIRouter(tags=["Real-time Monitoring"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 連線端點。前端透過 ws://.../api/v1/monitor/ws 建立連線。
    """
    # 1. 呼叫總機，接受連線並加入廣播名單
    await manager.connect(websocket)
    try:
        # 2. 保持連線開啟
        while True:
            # 儘管我們的架構主要是「後端單向推播給前端」，
            # 但這裡仍需要 receive_text() 來保持連線不中斷 (卡住迴圈)。
            # 未來也可以在這裡接收前端傳來的心跳包 (Ping) 或篩選指令。
            data = await websocket.receive_text()
            print(f"收到前端 WebSocket 訊息: {data}")
            
    except WebSocketDisconnect:
        # 3. 處理前端斷線事件
        manager.disconnect(websocket)
