from datetime import datetime, timedelta
import json
import paho.mqtt.client as mqtt
import sqlite3
from fastapi import FastAPI,WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
import time
from models import EstudianteData, ConnectionManager
from contextlib import contextmanager
import asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (get_swagger_ui_html)

app = FastAPI(
    title="API Home Automation Wizard",
    description="""This API is responsible for managing the home automation wizard's data and communication with MQTT broker.""",
    version= "0.1.0" 
)

app.mount("/static", StaticFiles(directory="static"), name="static")

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
    
    # si el topico contiene la palabra canal 
    if topic.find("canal") != -1:
        msj_json = json.loads(mensaje_recibido)
        print(msj_json)
        # Obtener el timestamp actual en el formato deseado
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        # Almacena los datos en la base de datos SQLite
        mensajeria_data["topico"] = msj_json['topico']
        mensajeria_data["mensaje"] = msj_json['mensaje']
        mensajeria_data['nombre'] = msj_json['nombre']
        print("mensajeria: ", mensajeria_data)
            
        
    else:
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
                # elif (topic == "door"):
            
                #     print("Mensaje recibido en", topic, ":", mensaje_recibido)
                #     mensaje_recibido_puerta = json.loads(mensaje_recibido)
                #     # comprobar si existe o no en la base de datos
                #     cursor.execute("SELECT * FROM actuadores WHERE id_led = ?", (mensaje_recibido_puerta['puerta_id'],))
                #     existing_puerta = cursor.fetchone()
                #     if existing_puerta:
                #         cursor.execute("UPDATE actuadores SET status = ? WHERE id_led = ?", (mensaje_recibido_puerta['set_status'],mensaje_recibido_puerta['puerta_id']))
                #     else:
                #         cursor.execute("INSERT INTO actuadores (id_led, status, topic) VALUES (?, ?, ?)", (mensaje_recibido_puerta['puerta_id'], mensaje_recibido_puerta['set_status'], topic))                
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


mqtt_client.subscribe('canal1')
mqtt_client.subscribe('canal2')
mqtt_client.subscribe('canal3')

#inicio del loop del cliente
mqtt_client.loop_start()

# Diccionario para almacenar mensajeria
mensajeria_data = {
    "topico":"",
    "mensaje":"",
    "nombre":"",
    "hora":""
}

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

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


# enviar mensajes en tiempo real que van llegando a mensajeria, junto con el nombre del usuario, a traves del rut del mensaje de un topico especifico
@app.websocket("/mensajeria/{topico}")
async def read_mensajeria(websocket:WebSocket,topico:str):
    await manager.connect(websocket)
    try:
        while True:
            data_json = await websocket.receive_text()
            data = json.loads(data_json)
            mensaje = data.get('mensaje')
            nombre = data.get('nombre')
            topico = data.get('topico')
            print(data_json)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        print("Desconectado")
        manager.disconnect(websocket)
        await manager.broadcast("Desconectado")
    
    # await manager.connect(websocket)
    # try:
    #     while True:
    #         if (mensajeria_data['topico'] != '' ):
    #             hora_m = time.strftime("%H:%M")
    #             data = {"topic":topico,"mensaje":mensajeria_data['mensaje'],"nombre":mensajeria_data['nombre'],"hora":hora_m}
    #             mensajeria_data.clear()
    #             print("mensajeria: ", mensajeria_data)
    #             await manager.broadcast(data)
    # except Exception:
    #     manager.disconnect(websocket)

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
    
@app.get("/controlar_puerta/set_status={set_status}&puerta_id={puerta_id}")
async def controlar_puerta(set_status:str,puerta_id:str):
    MQTT_MSG = json.dumps(
        {"set_status":set_status,"puerta_id":puerta_id},separators=(',', ':')
    )
    if(set_status == "OPEN"):
        mqtt_client.publish("door",MQTT_MSG)
        return {"message": "Puerta abierta correctamente"}
    elif (set_status == "CLOSE"):
        mqtt_client.publish("door",MQTT_MSG)
        return {"message": "Puerta cerrada correctamente"}
    else:
        return {"message": "Error en la petición, se esperaba OPEN o CLOSE."}
        
@app.post("/usuarios/verificar-usuario")
async def verificar_usuario(usuario: EstudianteData):
    # Conéctate a la base de datos SQLite
    conn = sqlite3.connect('home_automation_wizard.db')
    cursor = conn.cursor()

    # Verifica si el usuario ya existe en la base de datos
    cursor.execute('SELECT * FROM estudiante WHERE rut=?', (usuario.rut,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Si el usuario ya existe, notifica que ya existe
        conn.close()
        return {"mensaje": "El usuario ya existe en la base de datos.", "tipo": "Encontrado"}
    else:
        # Si el usuario no existe, agrégalo a la base de datos
        cursor.execute('INSERT INTO estudiante (rut, nombre, apellido, correo) VALUES (?, ?, ?, ?)',
                       (usuario.rut, usuario.nombre, usuario.apellido, usuario.correo))
        conn.commit()
        conn.close()

        # Notifica que el usuario fue agregado exitosamente
        return {"mensaje": "Usuario agregado exitosamente.", "tipo": "Creado"}

# obtener todas las preguntas
@app.get("/preguntas")
async def get_preguntas():
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM preguntas")
        preguntas = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]  # Obtiene los nombres de las columnas
        preguntas_data = []
        for pregunta in preguntas:
            pregunta_dict = dict(zip(column_names, pregunta))  # Combina los nombres de las columnas con los datos
            preguntas_data.append(pregunta_dict)
        return {"columnas": column_names, "preguntas": preguntas_data}
    
# Pregunta respondida por estudiante
@app.post("/preguntas/actualizar")
async def responder_pregunta(datos: dict):
    pregunta_id = datos.get('preguntaId')
    rut_usuario = datos.get('rutUsuario')
    if not pregunta_id or not rut_usuario:
        return {"mensaje": "Faltan datos en la petición.", "tipo": "Error"}
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM respuestas WHERE id_pregunta = ? AND rut = ?", (pregunta_id, rut_usuario))
        respuesta = cursor.fetchone()
        if respuesta:
            return {"mensaje": "El usuario ya ha respondido esta pregunta.", "tipo": "Encontrado"}
        else:
            cursor.execute("INSERT INTO respuestas (rut, id_pregunta, respuesta) VALUES (?, ?, ?)", (rut_usuario, pregunta_id, True))
            return {"mensaje": "Respuesta agregada exitosamente.", "tipo": "Creado"}
        
# obtener todas las respuestas
@app.get("/respuestas/{rutEstudiante}")
async def get_respuestas(rutEstudiante:str):
    with db_connection() as cursor:
        cursor.execute("SELECT id_pregunta FROM respuestas WHERE rut = ?", (rutEstudiante,))
        respuestas = cursor.fetchall()
    
    respuestas_lista = [respuesta[0] for respuesta in respuestas]
    print("respuestas",respuestas_lista)
    return {"respuestas":respuestas_lista}
