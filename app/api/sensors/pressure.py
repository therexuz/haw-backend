from fastapi import APIRouter, Depends
from ...mqtt.mqttClient import MQTTClient

router = APIRouter()

@router.get("/sensors/pressure")
def read_pressure(mqtt_client:MQTTClient = Depends(MQTTClient)):
    mqtt_client.test_connection()
    return {mqtt_client.get_last_message("test-result")}