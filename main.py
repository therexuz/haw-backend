from typing import Union
import paho.mqtt.client as mqtt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()
broker = '192.168.2.1'
port = 1883

origins =  [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def on_message(client, userdata, message):
    topic = message.topic
    mensaje_recibido = message.payload.decode()
    print("Mensaje recibido en", topic, ":", mensaje_recibido)
    # Almacena el último mensaje recibido en un diccionario global
    ultimos_mensajes[topic] = mensaje_recibido

# Configura el cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(broker)
mqtt_client.subscribe("temperatura")
mqtt_client.subscribe("humedad")
mqtt_client.subscribe("presion")
mqtt_client.subscribe("homewizard_mqtt")
mqtt_client.loop_start()

# Diccionario para almacenar los últimos mensajes de cada tópico
ultimos_mensajes = {
    "temperatura": "",
    "humedad": "",
    "presion": "",
    "homewizard_mqtt":""
}

@app.get("/temperatura")
async def read_temperature():
    return {"temperatura": ultimos_mensajes["temperatura"]}

@app.get("/humedad")
async def read_humidity():
    return {"humedad": ultimos_mensajes["humedad"]}

@app.get("/presion")
async def read_pressure():
    return {"presion": ultimos_mensajes["presion"]}

@app.get("/homewizard_mqtt")
async def homewizard_mqtt():
    return {"homewizard_mqtt": ultimos_mensajes["homewizard_mqtt"]}