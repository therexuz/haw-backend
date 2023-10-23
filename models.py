from pydantic import BaseModel
from fastapi import WebSocket
import time

class UserDataBase(BaseModel):
    rut: str
    digito_verificador: int
    nombre: str
    apellido: str
    email: str

class UserDataCreate(UserDataBase):
    pass

class UserData(UserDataBase):
    class Config:
        orm_mode = True

class SensorData(BaseModel):
    topic:str
    measure_time:str
    value:str
    
class ActuadorData(BaseModel):
    led_id:str
    set_status:str
    topic:str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)
    