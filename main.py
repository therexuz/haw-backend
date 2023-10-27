from datetime import datetime, timedelta
import json
import paho.mqtt.client as mqtt
import sqlite3
from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import time
from models import UserDataBase, UserDataCreate, SensorData, ConnectionManager
from contextlib import contextmanager
import asyncio
from pydantic import BaseModel

app = FastAPI()
broker = '192.168.2.1'
port = 1883

actuadores = ['leds','door','ventilation']
sensores = ['temperature','humidity','pressure','air_quality','light'] ## TODO:

manager = ConnectionManager()

init_db()

origins =  [
    "*"
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
    
    with db_connection() as cursor:
        if topic in actuadores:
            if (topic == "leds"):
                print("Mensaje recibido en", topic, ":", mensaje_recibido)
                mensaje_recibido_led = json.loads(mensaje_recibido)
                ultimos_mensajes["leds_status"][(mensaje_recibido_led['led_id'])] = (mensaje_recibido_led['set_status'])
                # comprobar si existe o no en la base de datos
                cursor.execute("SELECT * FROM actuadores WHERE id_led = ?", (mensaje_recibido_led['led_id'],))
                existing_led = cursor.fetchone()
                if existing_led:
                    cursor.execute("UPDATE actuadores SET status = ? WHERE id_led = ?", (mensaje_recibido_led['set_status'],mensaje_recibido_led['led_id']))
                else:
                    cursor.execute("INSERT INTO actuadores (id_led, status, topic) VALUES (?, ?, ?)", (mensaje_recibido_led['led_id'], mensaje_recibido_led['set_status'], topic))
        else:
            # Obtener el timestamp actual en el formato deseado
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
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
    "ventilation":"",
    "leds_status":{}
}

# Endpoint para testear conexión mqtt
@app.get("/test-mqtt-protocol")
async def test_mqtt_protocol():
    mqtt_client.publish("test-mqtt","test")
    return {"test-result":ultimos_mensajes["test-result"]}

@app.get("/estado-leds")
async def estado_leds():
    # Estado de leds en la base de datos de actuadores
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM actuadores WHERE topic = 'leds'")
        leds_status = cursor.fetchall()
        for led in leds_status:
            ultimos_mensajes["leds_status"][led[1]] = led[3]
    return {"leds_status":ultimos_mensajes["leds_status"]}


# Endpoints de los sensores
@app.websocket("/temperature")
async def read_temperature(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {"topic":"temperature","measure_time": time.strftime("%H:%M:%S"),"value":str(round(float(ultimos_mensajes["temperature"]),2))}
            await manager.broadcast(data)
            await asyncio.sleep(5)
    except Exception:
        manager.disconnect(websocket)
        
# obtener los datos de la ultima hora de datos de temperature
@app.get("/datos/tipo-sensor={tipo}")
async def get_last_hour_temperature(tipo:str):
    with db_connection() as cursor:
        hora_hace_una_hora = datetime.now() - timedelta(minutes=5)
        hora_hace_una_hora_str = hora_hace_una_hora.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT topic, time(timestamp), value FROM sensor_data WHERE topic = ? AND timestamp BETWEEN ? AND ?",
               (tipo, hora_hace_una_hora_str, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        # Obtener los nombres de las columnas
        column_names = [description[0] for description in cursor.description if description[0] != 'id']

        # Obtener los resultados de la consulta
        results = cursor.fetchall()

        formatted_results = [dict(zip(column_names, row)) for row in results]
        return {"last_hour_data":formatted_results}

@app.websocket("/air_quality")
async def read_air_quality(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {"topic":"air_quality","measure_time": time.strftime("%H:%M:%S"),"value":str(ultimos_mensajes["air_quality"])}
            await manager.broadcast(data)
            await asyncio.sleep(5)
    except Exception:
        manager.disconnect(websocket)

@app.websocket("/presion-atm")
async def read_atm_pressure(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {"topic":"pressure","measure_time": time.strftime("%H:%M:%S"),"value":str(ultimos_mensajes["pressure"])}
            await manager.broadcast(data)
            await asyncio.sleep(5)
    except Exception:
        manager.disconnect(websocket)

@app.websocket("/humidity")
async def read_humidity(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {"topic":"humidity","measure_time": time.strftime("%H:%M:%S"),"value":str(ultimos_mensajes["humidity"])}
            await manager.broadcast(data)
            await asyncio.sleep(5)
    except Exception:
        manager.disconnect(websocket)

@app.websocket("/light")
async def read_light_level(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = {"topic":"light_sensor","measure_time": time.strftime("%H:%M:%S"),"value":str(ultimos_mensajes["light"])}
            await manager.broadcast(data)
            await asyncio.sleep(5)
    except Exception:
        manager.disconnect(websocket)
        
# Endpoints de los actuadores
@app.get("/controlar_leds/set_status={set_status}&led_id={led_id}")
async def control_leds(set_status:str,led_id:str):
    MQTT_MSG = json.dumps(
        {"set_status":set_status,"led_id":led_id},separators=(',', ':')
    )
    if(set_status == "ON"):
        mqtt_client.publish("leds",MQTT_MSG)
        return {"message": "Luz encendida correctamente"}
    elif (set_status == "OFF"):
        mqtt_client.publish("leds",MQTT_MSG)
        return {"message": "Luz apagada correctamente"}
    else:
        return {"message": "Error en la petición, se esperaba ON o OFF."}
    
@app.post("/login")
async def login_or_create_user(user_data:UserDataCreate):

    with db_connection() as cursor:

        cursor.execute("SELECT id FROM user_data WHERE rut = ?", (user_data.rut,))
        existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400,detail="Usuario ya registrado")
    
    with db_connection as cursor:
        cursor.execute("INSERT INTO user_data (rut, digito_verificador, nombre, apellido, email) VALUES (?, ?, ?, ?, ?)", (user_data.rut, user_data.digito_verificador, user_data.nombre,user_data.apellido,user_data.email))

    return Response(content="Usuario registrado con éxito", status_code=200)