import paho.mqtt.client as mqtt
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()
broker = '192.168.1.83'
port = 1883

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

# Suscipción a tópicos de test
mqtt_client.subscribe("test-result")
mqtt_client.subscribe("test-mqtt")

# Suscripción a tópicos de sensores
mqtt_client.subscribe("temperature")
mqtt_client.subscribe("humidity")
mqtt_client.subscribe("pressure")
mqtt_client.subscribe("air_quality")
mqtt_client.subscribe("light")

# Suscripción a tópicos de actuadores
mqtt_client.subscribe("leds")
mqtt_client.subscribe("door")
mqtt_client.subscribe("ventilation")

#inicio del loop del cliente
mqtt_client.loop_start()

# Diccionario para almacenar los últimos mensajes de cada tópico
ultimos_mensajes = {
    "temperature": "",
    "humidity": "",
    "pressure": "",
    "air_quality":"",
    "test-result":"",
    "leds":"",
    "door":"",
    "ventilation":""
}

# Endpoint para testear conexión mqtt
@app.get("/test-mqtt-protocol")
async def test_mqtt_protocol():
    mqtt_client.publish("test-mqtt","test")
    time.sleep(1) # wait
    return {"test-result":ultimos_mensajes["test-result"]}

# Endpoints de los sensores
@app.get("/temperatura")
async def read_temperature():
    return {"temperatura": ultimos_mensajes["temperature"]}

@app.get("/calidad-aire")
async def read_temperature():
    return {"calidad_aire": ultimos_mensajes["air_quality"]}

@app.get("/presion-atm")
async def read_temperature():
    return {"presion_atm": ultimos_mensajes["pressure"]}

@app.get("/humedad")
async def read_humidity():
    return {"humedad": ultimos_mensajes["humidity"]}

# Endpoints de los actuadores
@app.get("/encender_led={set_status}&{led_id}")
async def control_leds(set_status:str,led_id:str):
    if(set_status == "ON"):
        mqtt_client.publish("leds","ON " + led_id)
        return Response(content="Luz encendida correctamente", status_code=200)
    elif (set_status == "OFF"):
        mqtt_client.publish("leds","OFF " + led_id)
        return Response(content="Luz apagada correctamente", status_code=200)
    else:
        return Response(content="Error en la peticion, se esperaba ON o OFF.", status_code=400)