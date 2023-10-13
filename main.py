import paho.mqtt.client as mqtt
import sqlite3
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import time
from models import UserDataBase, UserDataCreate
from contextlib import contextmanager

app = FastAPI()
broker = '192.168.1.83'
port = 1883

init_db()

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

# Función para crear una conexión a la base de datos
@contextmanager
def db_connection():
    conn = sqlite3.connect('home_automation_wizard.db')
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.commit()
        conn.close()

def on_message(client, userdata, message):
    topic = message.topic
    mensaje_recibido = message.payload.decode()
    print("Mensaje recibido en", topic, ":", mensaje_recibido)

    # Obtener el timestamp actual en el formato deseado
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with db_connection() as cursor:

        # Almacena los datos en la base de datos SQLite
        cursor.execute("INSERT INTO sensor_data (topic, timestamp, value) VALUES (?, ?, ?)", (topic, timestamp, mensaje_recibido))
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
    "light":"",
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
async def read_air_quality():
    return {"calidad_aire": ultimos_mensajes["air_quality"]}

@app.get("/presion-atm")
async def read_atm_pressure():
    return {"presion_atm": ultimos_mensajes["pressure"]}

@app.get("/humedad")
async def read_humidity():
    return {"humedad": ultimos_mensajes["humidity"]}

@app.get("/sensor-luz")
async def read_light_level():
    return {"light_sensor": ultimos_mensajes["light"]}

# Endpoints de los actuadores
@app.get("/controlar_leds/set_status={set_status}&led_id={led_id}")
async def control_leds(set_status:str,led_id:str):
    if(set_status == "ON"):
        mqtt_client.publish("leds","ON " + led_id)
        return Response(content="Luz encendida correctamente", status_code=200)
    elif (set_status == "OFF"):
        mqtt_client.publish("leds","OFF " + led_id)
        return Response(content="Luz apagada correctamente", status_code=200)
    else:
        return Response(content="Error en la peticion, se esperaba ON o OFF.", status_code=400)
    
@app.post("/login")
async def registrar_usuario(user_data:UserDataCreate):

    with db_connection() as cursor:

        cursor.execute("SELECT id FROM user_data WHERE rut = ?", (user_data.rut,))
        existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400,detail="Usuario ya registrado")
    
    with db_connection as cursor:
        cursor.execute("INSERT INTO user_data (rut, digito_verificador, nombre, apellido, email) VALUES (?, ?, ?, ?, ?)", (user_data.rut, user_data.digito_verificador, user_data.nombre,user_data.apellido,user_data.email))

    return Response(content="Usuario registrado con éxito", status_code=200)