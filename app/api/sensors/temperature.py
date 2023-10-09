from fastapi import APIRouter
from ...mqtt.mqttClient import MQTTClient

router = APIRouter()

@router.get("/sensors/temperature/")
async def read_temperature():
    mqtt_client = MQTTClient("192.168.1.83",1883)
    mqtt_client.test_connection()
    return {mqtt_client.get_last_message("test-result")}
