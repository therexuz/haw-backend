from typing import Optional
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect
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
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, topic: str):
        print(f"connect to {topic}")
        await websocket.accept()

        if topic not in self.active_connections:
            self.active_connections[topic] = set()

        self.active_connections[topic].add(websocket)

    async def disconnect(self, topic: str, websocket: WebSocket):
        print(f"disconnect from {topic}")
        await websocket.close()
        self.active_connections[topic].remove(websocket)

    async def broadcast(self, topic: str, message):
        print(f"broadcast to {topic}")
        if topic in self.active_connections:
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    pass  # No es necesario manejar explícitamente la desconexión aquí, ya que se maneja en ConnectionManager
    