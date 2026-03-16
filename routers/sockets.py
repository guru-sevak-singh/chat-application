from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
# from message_queue.message_queue import message_queue

# import redis.asyncio as aioredis
# import asyncio
# import json
from database import SessionalMaker
from models import Messages
from utils import decode_token


router = APIRouter(
    tags=['Web Socket']
)

class ConnectionManager:
    def __init__(self):
        self.activate_connections : list[WebSocket] = []
    
    async def connect(self, websocket : WebSocket):
        await websocket.accept()
        self.activate_connections.append(websocket)

    def disconnect(self, websocket : WebSocket):
        self.activate_connections.remove(websocket)

    async def broadcast(self, message : str, sender : WebSocket):
        for connection in self.activate_connections:
            if connection != sender:
                await connection.send_json(message)

manager = ConnectionManager()




@router.websocket("/ws/")
async def room_socket(websocket : WebSocket, token : str = Query(...)):
    user_details = decode_token(token.split()[1])
    db = SessionalMaker()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            message = Messages(
                context=data['message'],
                room_id=data['room_id'],
                sender_id=user_details.id
            )
            db.add(message)
            db.commit()

            await manager.broadcast(data, sender=websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        db.close()

