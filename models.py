from typing import Optional
from pydantic import BaseModel
from fastapi import WebSocket
import time

class UserDataBase(BaseModel):
    rut: str
    nombre: str
    apellido: str
    correo: Optional[str] = None

class UserDataCreate(UserDataBase):
    pass

# class UserData(UserDataBase):
#     class Config:
#         orm_mode = True

class SensorData(BaseModel):
    topic:str
    measure_time:str
    value:str
    
class ActuadorData(BaseModel):
    led_id:str
    set_status:str
    topic:str
    
class EstudianteData(BaseModel):
    rut:str
    nombre:str
    apellido:str
    correo:Optional[str] = None
    
class PreguntaData(BaseModel):
    tipo:str
    pregunta:str
    respuesta:str
    alternativas:str

class RespuestaData(BaseModel):
    rut:str
    id_pregunta:int
    respuesta:bool
    
class MensajeriaData(BaseModel):
    topico:str
    mensaje:str
    nombre:str
    timestamp:str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        print("connect")
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        print("disconnect")
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: WebSocket):
        print("send_personal_message")
        await websocket.send_json(message)

    async def broadcast(self, message):
        print("broadcast")
        for connection in self.active_connections:
            await connection.send_json(message)
    