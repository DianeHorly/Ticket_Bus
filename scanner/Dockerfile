# Ce dockerfile est utilisé pour créer une image Docker pour le scanner MQTT.
FROM python:3.13-slim

WORKDIR /app

COPY scanner_mqtt.py .

RUN pip install paho-mqtt

CMD ["python", "scanner_mqtt.py"]
