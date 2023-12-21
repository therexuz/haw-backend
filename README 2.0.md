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

## Tener en cuenta

- El nombre del directorio raiz para este ejemplo es `ha_wizard`, cambiar en caso que sea distinto.

## Instalación

1. Clona este repositorio en tu Raspberry Pi 3:

   ```bash
      git clone https://github.com/therexuz/haw-backend.git /home/ha_wizard/haw-backend
      cd haw-backend
   ```

2. Instala las bibliotecas necesarias:

   ```bash
      pip install -r /home/ha_wizard/haw-backend/requirements.txt
   ```

3. Para probar el funcionamiento, ejecuta la API de la siguiente manera:

   ```bash
      python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   ó

   ```bash
      uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Instalar Mosquitto

1. Instalación
   1. Ejecutar el comando para actualizar las dependencias

      ```bash
         sudo apt update && sudo apt upgrade
      ```

   2. Instalación

      ``` bash
         sudo apt install -y mosquitto mosquitto-clients
      ```

2. Mosquitto como Servicio
   1. Habilitar el servicio de Mosquitto

      ```bash
         sudo systemctl enable mosquitto.service
      ```

   2. Configuracion

      ```bash
         sudo sh -c 'echo "listener 1883\nallow_anonymous true" >> /etc/mosquitto/mosquitto.conf'
      ```

   3. Reiniciar

      ```bash
         sudo systemctl restart mosquitto
      ```

## Ejecutar como servicio (systemctl) el Backend

1. Crear archivo de servicio y agregar configuracion:

   ```bash
      sudo tee /etc/systemd/system/haw-backend.service > /dev/null <<EOL
      [Unit]
      Description=Home Automation Wizard API

      [Service]
      WorkingDirectory=/home/ha_wizard/haw-backend
      ExecStart=uvicorn main:app --reload --host 0.0.0.0 --port 8000

      [Install]
      WantedBy=multi-user.target
      EOL
   ```

2. Configuracion
   1. Recargar los servicios

      ```bash
         sudo systemctl daemon-reload
      ```

   2. Reiniciar el servicio haw-backend
   Ejecutar los siguientes comandos

      ```bash
         sudo systemctl start haw-backend.service
      ```

      ```bash
         sudo systemctl restart haw-backend.service
      ```

3. Verificar el estado del servicio haw-backend

   ```bash
      sudo systemctl status haw-backend.service
   ```

## Uso

Ejecuta el servicio en tu Raspberry Pi 3. La API estará disponible en <http://localhost:puerto>. Puedes acceder a los datos a través de la API o configurar tus dispositivos IoT para publicar datos en el broker MQTT en la misma Raspberry Pi.
