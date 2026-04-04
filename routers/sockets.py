from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
# from message_queue.message_queue import message_queue

# import redis.asyncio as aioredis
# import asyncio
# import json
from database import SessionalMaker
from models import Messages
from utils import decode_token


router = APIRouter(
    prefix='/ws',
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


class RtcManager:
    def __init__(self):
        self.active_connections : dict[str, WebSocket] = {}
    
    async def connect(self, user_id : str, websocket : WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id : str):
        self.active_connections.pop(user_id, None)

rtc_manager = RtcManager()

class VideoRtcManager:
    def __init__(self):
        self.active_connections : dict[str, WebSocket] = {}
    
    async def connect(self, user_id : str, websocket : WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id : str):
        self.active_connections.pop(user_id, None)

video_rtc_manager = VideoRtcManager()


@router.websocket("/")
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

@router.websocket("/rtc/{phone_number}")
async def rtc_socket(websocket : WebSocket, phone_number : str):
    await rtc_manager.connect(phone_number, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            match msg_type:
                case "call-request":
                    to = data.get("to")

                    if to in rtc_manager.active_connections:
                        target_websocket = rtc_manager.active_connections[to]
                        await target_websocket.send_json({
                            "type": "incoming-call",
                            "from": phone_number
                        })
                    
                    else:
                        await websocket.send_json({
                            "type": "call-error",
                            "message": f"User with phone number {to} is not available Right Now"
                        })
                
                case "call-reject":
                    phon = data.get("phone_number")
                    if phon in rtc_manager.active_connections:
                        target_websocket = rtc_manager.active_connections[phon]
                        await target_websocket.send_json({
                            "type": "call-rejected",
                            "from": phone_number
                        })
                
                case "call-accept":
                    phon = data.get("target")
                    if phon in rtc_manager.active_connections:
                        target_websocket = rtc_manager.active_connections.get(phon, None)
                        if target_websocket:
                            await target_websocket.send_json({
                                "type": "call-accepted",
                                "from": phone_number
                            })
                
                case "offer":
                    target = data.get("target")
                    if target in rtc_manager.active_connections:
                        target_websocket = rtc_manager.active_connections.get(target, None)
                        if target_websocket:
                            await target_websocket.send_json({
                                **data,
                                "from": phone_number
                            })
                    else:
                        await websocket.send_json({
                            "type": "call-error",
                            "message": f"User with phone number {target} is not available Right Now"
                        })
                
                case "answer":
                    target = data.get("target")
                    target_websocket = rtc_manager.active_connections.get(target, None)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                    else:
                        await websocket.send_json({
                            "type": "call-error",
                            "message": f"User with phone number {target} is not available Right Now"
                        })
                
                case "ice-candidate":
                    target = data.get("target")
                    target_websocket = rtc_manager.active_connections.get(target, None)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                    else:
                        await websocket.send_json({
                            "type": "call-error",
                            "message": f"User with phone number {target} is not available Right Now"
                        })


    except WebSocketDisconnect:
        rtc_manager.disconnect(phone_number)

@router.websocket("/video-call/{phone_number}")
async def video_rtc_socket(websocket : WebSocket, phone_number : str):
    await video_rtc_manager.connect(phone_number, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            match msg_type:
                case "call-request":
                    to = data.get("to")
                    target_websocket = video_rtc_manager.active_connections.get(to)
                    if target_websocket:
                        await target_websocket.send_json(
                            {
                                "type": "incoming-call",
                                "from": phone_number
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "msg": f"Person with phone number : {to} is not online, Try after some time"
                            }
                        )
                
                case "call-reject":
                    whose = data.get("whose")
                    target_websocket = video_rtc_manager.active_connections.get(whose)
                    if target_websocket:
                        await target_websocket.send_json(
                            {
                                "type": "call-reject",
                                "by": phone_number
                            }
                        )
                
                case "call-accept":
                    targetId = data.get("targetId")
                    target_websocket = video_rtc_manager.active_connections.get(targetId)
                    if target_websocket:
                        await target_websocket.send_json({
                            "type": "call-accepted",
                            "from": phone_number
                        })
                
                case "offer":
                    targetId = data.get("targetId")
                    
                    target_websocket = video_rtc_manager.active_connections.get(targetId)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                
                case "answer":
                    targetId = data.get("targetId")
                    target_websocket = video_rtc_manager.active_connections.get(targetId)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                
                case "ice-candidate":
                    targetId = data.get("targetId")
                    target_websocket = video_rtc_manager.active_connections.get(targetId)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                
                case "call-end":
                    targetId = data.get("targetId")
                    target_websocket = video_rtc_manager.active_connections.get(targetId)
                    if target_websocket:
                        await target_websocket.send_json({
                            **data,
                            "from": phone_number
                        })
                    
            
    except WebSocketDisconnect:
        video_rtc_manager.disconnect(phone_number)
    except Exception as e:
        print(f"Error in video RTC socket: {e}")
