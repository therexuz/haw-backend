from fastapi import APIRouter, Depends
from ...mqtt.mqttClient import MQTTClient

router = APIRouter()

@router.get("/sensors/temperature/")
async def read_temperature(mqtt_client:MQTTClient = Depends(MQTTClient)):
    return {mqtt_client.get_last_message("temperature")}
