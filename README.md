# Proyecto IoT y domótica con Raspberry Pi 3 "Home Automation Wizard"

Este proyecto tiene como objetivo crear una solución IoT utilizando una Raspberry Pi 3 como servidor central. La Raspberry Pi 3 alojará una API que recopila datos de sensores y los publica a través de MQTT. Además, el broker MQTT se ejecutará localmente para recibir datos de dispositivos como ESP32 a través de la red.

## Características

- Recopila y almacena datos de sensores.
- Comunica datos a través de MQTT.
- Interfaz de API para acceder a los datos.
- Ejecución como un servicio en systemd (systemctl).
- Integración con dispositivos IoT como ESP32.

## Requisitos

- Raspberry Pi 3
- Python 3.x
- Bibliotecas adicionales (lista de requisitos)
- Dispositivos IoT compatibles (por ejemplo, ESP32)
- Broker MQTT (por ejemplo, Mosquitto)

## Instalación

1. Clona este repositorio en tu Raspberry Pi 3:

```bash
   git https://github.com/therexuz/haw-backend.git
   cd haw-backend
```

2. Instala las bibliotecas necesarias:

```bash
   pip install -r requirements.txt
```

3. Para probar el funcionamiento, ejecuta la API de la siguiente manera:

```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

ó

```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

 
 ## Ejecutar como servicio (systemctl)

1. Crear archivo de servicio:
```bash
   sudo nano haw-backend.service
```

2. Escribir los parámetros de configuración para el servicio. Por ejemplo: 

```
   [Unit]
   Description=Home Automation Wizard API

   [Service]
   WorkingDirectory=/ruta/a/la/carpeta/API #Ej.
   ExecStart=uvicorn main:app --reload --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
```

3. Configura y ejecuta el servicio en systemd:

```bash
    sudo cp haw-backend.service /etc/systemd/system/
    sudo systemctl enable haw-backend.service
    sudo systemctl start haw-backend.service
```

## Uso

Ejecuta el servicio en tu Raspberry Pi 3. La API estará disponible en http://localhost:puerto. Puedes acceder a los datos a través de la API o configurar tus dispositivos IoT para publicar datos en el broker MQTT en la misma Raspberry Pi.
