import paho.mqtt.client as mqtt
import time

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("192.168.1.83", 1883)
        self.client.loop_start()

        # Diccionario para almacenar los últimos mensajes de cada tópico
        self.ultimos_mensajes = {
            "temperature": "",
            "humidity": "",
            "pressure": "",
            "air_quality": "",
            "light": "",
            "door": "",
            "leds":"",
            "ventilation":"",
            "test-result":"",
        }

        # Suscripciones iniciales
        self.client.subscribe("temperature")
        self.client.subscribe("humidity")
        self.client.subscribe("pressure")
        self.client.subscribe("air_quality")
        self.client.subscribe("light")
        self.client.subscribe("door")
        self.client.subscribe("leds")
        self.client.subscribe("ventilation")
        self.client.subscribe("test-result")

    def on_message(self, client, userdata, message):
        topic = message.topic
        mensaje_recibido = message.payload.decode()
        print("Mensaje recibido en", topic, ":", mensaje_recibido)
        # Almacena el último mensaje recibido en un diccionario global
        self.ultimos_mensajes[topic] = mensaje_recibido

    def publish_message(self, topic, message):
        self.client.publish(topic, message)
        # Agrega una pequeña pausa para permitir que el mensaje se envíe antes de continuar
        time.sleep(1)

    def get_last_message(self, topic):
        return self.ultimos_mensajes.get(topic, "")
    
    def test_connection(self):
        self.client.publish("test-mqtt","test")
        time.sleep(1)
    
    def disconnect(self):
        self.client.disconnect()

def get_mqtt_client():
    broker = "192.168.1.83"
    port = 1883
    mqtt_client = MQTTClient(broker,port)
    return mqtt_client
