from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from .application import templates
import json

router = APIRouter(
    prefix='/web-rtc',
    tags=['Web RTC']
)

connected_users = {}


@router.get("/")
async def render_rtc_template(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("web-rtc.html", context)

@router.websocket("/{user_id}")
async def rtc_endpoint(websocket : WebSocket, user_id : str):
    # once check whether that user is already connected or not
    if connected_users.get(user_id) != None:
        del connected_users[user_id]

    # step 1 accept the connecction
    await websocket.accept()
    connected_users[user_id] = websocket

    # tell the same user that you are connected successfully
    await websocket.send_text(
        json.dumps(
            {
                "type": "connection-success",
                "message": "Your are connected successfyllt",
                "total_users": len(connected_users)
            }
        )
    )

    # Add this — tell the new user who is already online
    await websocket.send_text(json.dumps({
        "type": "online-users",
        "users": [u_id for u_id in connected_users if u_id != user_id]
    }))


    # tell every one who are connected to this websocket
    for u_id, wb in connected_users.items():
        if u_id != user_id:
            await wb.send_text(
                json.dumps(
                    {
                        "type": "new-connection",
                        "user_id" : user_id
                    }
                )
            )
    
    # keep listining the message from the user
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            msg_type = message.get("type")

            if msg_type == "call-request":
                target_id = message.get('target')
                if target_id in connected_users:
                    target_websocket = connected_users.get(target_id)
                    await target_websocket.send_text(
                        json.dumps(
                            {
                                "type": 'incoming-call',
                                "from" : user_id
                            }
                        )
                    )

                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message" : f"User {target_id} not found."
                            }
                        )
                    )
            
            elif msg_type == "call-rejected":
                target_id = connected_users.get("target")
                if target_id not in connected_users:
                    target_websocket = connected_users[target_id]
                    await target_websocket.send_text(
                        json.dumps(
                            {
                                "type": "call-rejected",
                                "from": user_id
                            }
                        )
                    )
            
            elif msg_type == "offer":
                target_id = message.get("target")
                if target_id in connected_users:
                    target_websocket = connected_users.get(target_id)

                    await target_websocket.send_text(
                        json.dumps({
                            **message,
                            "from": user_id
                        })
                    )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type" : "error",
                                "message": f"User {target_id} not found"
                            }
                        )
                    )

            elif msg_type == "answer":
                target_id = message.get("target")
                if target_id in connected_users:
                    target_websocket = connected_users.get(target_id)
                    await target_websocket.send_text(
                        json.dumps({
                            **message,
                            "from" : user_id
                        })
                    )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message" : f"User {target_id} not found"
                            }
                        )
                    )
            
            elif msg_type == "ice-candidate":
                target_id = message.get("target")
                if target_id in connected_users:
                    target_websocket = connected_users.get(target_id)
                    await target_websocket.send_text(
                        json.dumps({
                            **message,
                            "from": user_id
                        })
                    )

                else:
                    await websocket.send_text(
                        json.dumps({
                            "type" : "error",
                            "message": f"User {target_id} not found"
                        })
                    )


            # send the data to everyone except this user
            for u_id, wb in connected_users.items():
                if u_id != user_id:
                    await wb.send_text(
                        json.dumps(
                            message
                        )
                    )

    except WebSocketDisconnect:
        del connected_users[user_id]

        # tell everyone that this user is now disconnected
        for u_id, wb in connected_users.items():
            if u_id != user_id:
                await wb.send_text(
                    json.dumps(
                        {
                            "type": "user-disconnect",
                            "user_id" : user_id
                        }
                    )
                )
    
    # except Exception as e:
    #     print("\n"*5, "error => ", e, "\n" * 3)