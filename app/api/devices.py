# En un archivo de tu módulo "api", por ejemplo, "devices.py"
import json
from fastapi import APIRouter
from typing import Dict, List

router = APIRouter()

devices_db = []  # Lista de dispositivos (inicialmente vacía)

@router.post("/admin/devices", response_model=Dict[str, str])
def create_device(device_info: Dict[str, str]):
    # Agregar el nuevo dispositivo a la lista de dispositivos
    devices_db.append(device_info)
    save_devices_to_json()
    return {"message": "Dispositivo registrado exitosamente"}

@router.get("/admin/devices", response_model=List[Dict[str, str]])
def get_devices():
    return devices_db

@router.put("/admin/devices/{device_id}", response_model=Dict[str, str])
def update_device(device_id: int, updated_device_info: Dict[str, str]):
    # Realizar la actualización del dispositivo por su ID
    # (Implementa la lógica según tus necesidades)
    save_devices_to_json()
    return {"message": "Dispositivo actualizado exitosamente"}

@router.delete("/admin/devices/{device_id}", response_model=Dict[str, str])
def delete_device(device_id: int):
    # Eliminar el dispositivo por su ID
    # (Implementa la lógica según tus necesidades)
    save_devices_to_json()
    return {"message": "Dispositivo eliminado exitosamente"}

def save_devices_to_json():
    # Guardar la lista de dispositivos actualizada en un archivo JSON
    with open("devices.json", "w") as json_file:
        json.dump(devices_db, json_file)