#   scanner/scanner_mqtt.py

import paho.mqtt.client as mqtt
import json
import time

BROKER = "localhost"
PORT = 1883
TOPIC = "bus_app/scan"

def scanner(ticket_id):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    # Construire le message
    message = {
        "ticket_id": ticket_id
    }

    # Publier le message
    client.publish(TOPIC, json.dumps(message))
    print(f" Ticket scanné et envoyé: {message}")

    client.disconnect()

if __name__ == "__main__":
    # Simule un scan
    ticket_id = input(" Entrez l'ID du ticket à scanner: ")
    scanner(ticket_id)
