from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # 用一個 List 來儲存所有目前活躍的 WebSocket 連線
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受前端的連線請求，並加入廣播名單"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新連線建立。目前活躍連線數：{len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """前端斷線時，將其從廣播名單中移除"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"連線中斷。目前活躍連線數：{len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """將資料推播給所有活躍的連線"""
        # 因為連線隨時可能中斷，所以需要用 try-except 保護推播過程
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"推播失敗，移除失效連線: {e}")
                self.disconnect(connection)

# 實例化一個全域的 manager，讓整個應用程式共用同一個電台總機
manager = ConnectionManager()
