from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .app.api.actuators import door, camera,leds, ventilation
from .app.api.sensors import temperature,humidity,light,pressure,air_quality
from .app.api import devices
from .app import main

app = FastAPI()

origins =  [
    "http://192.168.2.1:8080",
    "http://192.168.2.2:8080",
    "http://192.168.1.92:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Registrar las rutas de cada módulo en la aplicación FastAPI

# RUTAS DE LOS SENSORES
app.include_router(temperature.router)
app.include_router(humidity.router)
app.include_router(pressure.router)
app.include_router(light.router)
app.include_router(pressure.router)

# RUTAS DE LOS ACTUADORES
app.include_router(door.router)
app.include_router(leds.router)
app.include_router(camera.router)
app.include_router(air_quality)
app.include_router(ventilation.router)

# RUTAS DE ADMINISTRACIÓN
app.include_router(devices.router)

# from typing import Union
# import paho.mqtt.client as mqtt
# from fastapi import FastAPI
# 
# import time
# from pydantic import BaseModel

# app = FastAPI()
# broker = '192.168.2.1'
# port = 1883

# def on_message(client, userdata, message):
#     topic = message.topic
#     mensaje_recibido = message.payload.decode()
#     print("Mensaje recibido en", topic, ":", mensaje_recibido)
#     # Almacena el último mensaje recibido en un diccionario global
#     ultimos_mensajes[topic] = mensaje_recibido

# # Configura el cliente MQTT
# mqtt_client = mqtt.Client()
# mqtt_client.on_message = on_message
# mqtt_client.connect(broker)
# mqtt_client.subscribe("temperatura")
# mqtt_client.subscribe("humedad")
# mqtt_client.subscribe("presion")
# mqtt_client.subscribe("homewizard_mqtt")
# mqtt_client.subscribe("test-result")
# mqtt_client.subscribe("luces")
# mqtt_client.loop_start()

# # Diccionario para almacenar los últimos mensajes de cada tópico
# ultimos_mensajes = {
#     "temperatura": "",
#     "humedad": "",
#     "presion": "",
#     "homewizard_mqtt":"",
#     "test-result":"",
#     "luces":""
# }

# class Led(BaseModel):
#     text: str

# @app.get("/temperatura")
# async def read_temperature():
#     return {"temperatura": ultimos_mensajes["temperatura"]}

# @app.get("/humedad")
# async def read_humidity():
#     return {"humedad": ultimos_mensajes["humedad"]}

# @app.get("/presion")
# async def read_pressure():
#     return {"presion": ultimos_mensajes["presion"]}

# @app.get("/homewizard_mqtt")
# async def homewizard_mqtt():
#     return {"homewizard_mqtt": ultimos_mensajes["homewizard_mqtt"]}

# @app.get("/test-mqtt-protocol")
# async def test_mqtt_protocol():
#     mqtt_client.publish("test-mqtt","test")
#     time.sleep(1) # wait
#     return {"test-result":ultimos_mensajes["test-result"]}

# @app.post("/controlar-leds")
# async def turn_on_led(data:Led):
#     mqtt_client.publish("luces","ON")
#     time.sleep(1)
#     return {"luces":ultimos_mensajes["luces"] + data.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)