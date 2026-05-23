from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class RoomManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, room_id, username, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = []

        self.rooms[room_id].append({
            "username": username,
            "websocket": websocket
        })

        await self.broadcast(
            room_id,
            {
                "type": "join",
                "username": username,
                "room_id": room_id
            }
        )
    
    async def disconnect(self, room_id, username, websocket):
        if room_id not in self.rooms:
            return
        
        self.rooms[room_id] = [
            connection for connection in self.rooms[room_id] if connection["websocket"] != websocket
        ]

        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self, room_id, payload):
        if room_id not in self.rooms:
            return
        
        for connection in self.rooms[room_id]:
            await connection["websocket"].send_json(payload)

    def get_users(self, room_id):
        if room_id not in self.rooms:
            return []
        
        return [
            connection["username"] for connection in self.rooms[room_id]
        ]

manager = RoomManager()

@app.websocket('/ws/rooms/{room_id}')
async def websocket_chat(websocket: WebSocket, room_id: str):
    username = websocket.query_params.get("username")

    if username is None or not username.strip():
        await websocket.close(code=1008)
        return
    
    await manager.connect(room_id, username, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                text = data["text"]

                if len(text) > 300:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long (you are too long :D)"
                    })
                    continue

                await manager.broadcast(
                    room_id,
                    {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    }
                )

    except WebSocketDisconnect:
        await manager.disconnect(
            room_id,
            username,
            websocket
        )

@app.get('/rooms/{room_id}/users')
async def get_room_users(room_id: str):
    return {
        "room_id": room_id,
        "users": manager.get_users(room_id)
    }
