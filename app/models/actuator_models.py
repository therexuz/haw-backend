from pydantic import BaseModel

class TemperatureSensorData(BaseModel):
    value: float
    unit: str
    timestamp: str

class HumiditySensorData(BaseModel):
    value: float
    unit: str
    timestamp: str

class LightSensorData(BaseModel):
    value: float
    unit: str
    timestamp: str

class AirQualitySensorData(BaseModel):
    pm25: float
    pm10: float
    co2: int
    timestamp: str

class PressureSensorData(BaseModel):
    value: float
    unit: str
    timestamp: str