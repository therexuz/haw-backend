# Proyecto IoT con Raspberry Pi 3

Este proyecto tiene como objetivo crear una solución IoT utilizando una Raspberry Pi 3 como servidor central. La Raspberry Pi 3 alojará una API que recopila datos de sensores y los publica a través de MQTT. Además, el broker MQTT se ejecutará localmente para recibir datos de dispositivos como ESP32 a través de la red.

## Características

- Recopila y almacena datos de sensores.
- Comunica datos a través de MQTT.
- Interfaz de API para acceder a los datos.
- Ejecución como un servicio en systemd (systemctl).
- Integración con dispositivos IoT como ESP32.

## Capturas de Pantalla

(Si es relevante, puedes incluir capturas de pantalla de la interfaz de la API o diagramas de arquitectura aquí).

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

3. Configura y ejecuta el servicio en systemd:

```bash
    sudo cp tu-servicio.service /etc/systemd/system/
    sudo systemctl enable tu-servicio
    sudo systemctl start tu-servicio
```

## Uso

Ejecuta el servicio en tu Raspberry Pi 3. La API estará disponible en http://localhost:puerto. Puedes acceder a los datos a través de la API o configurar tus dispositivos IoT para publicar datos en el broker MQTT en la misma Raspberry Pi.