# app/mqtt_client.py

import json
from bson.objectid import ObjectId  # Pour manipuler les ObjectId MongoDB
from pymongo import MongoClient     # Client MongoDB pour accéder à la base de données
import paho.mqtt.client as mqtt     # Client MQTT pour la communication avec le broker

# Configuration du broker MQTT (adresse et port)
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "bus_app/scan"  # Topic sur lequel on écoute les scans de tickets

# Fonction appelée lors de la connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print(f" Connecté au broker MQTT avec le code de retour {rc}")
    # Souscription au topic défini pour recevoir les messages
    client.subscribe(MQTT_TOPIC)

# Fonction appelée lorsqu'un message est reçu sur le topic MQTT
def on_message(client, userdata, msg):
    print(f" Message reçu sur le topic {msg.topic} : {msg.payload.decode()}")

    try:
        # Décodage du message JSON reçu (payload)
        data = json.loads(msg.payload.decode())
        ticket_id = data.get("ticket_id")

        if not ticket_id:
            # Si aucun ticket_id dans le message, on stoppe le traitement
            print(" Aucun ticket_id trouvé dans le message.")
            return

        # Connexion à la base MongoDB locale
        mongo = MongoClient("mongodb://localhost:27017/")
        db = mongo["bus_app"]
        tickets_collection = db["tickets"]

        # Recherche du ticket dans la collection via son _id (ObjectId MongoDB)
        ticket = tickets_collection.find_one({"_id": ObjectId(ticket_id)})

        if not ticket:
            # Ticket non trouvé en base, on log l'erreur
            print(f" Ticket {ticket_id} non trouvé.")
            return

        # Vérifie si le ticket est déjà validé
        if ticket.get("valide"):
            print(f" Ticket {ticket_id} est déjà validé.")
        else:
            # Met à jour le ticket pour le marquer comme validé
            tickets_collection.update_one(
                {"_id": ObjectId(ticket_id)},
                {"$set": {"valide": True}}
            )
            print(f" Ticket {ticket_id} validé avec succès.")

    except Exception as e:
        # Gestion des erreurs lors du traitement du message MQTT
        print(f" Erreur lors du traitement du message MQTT : {e}")

# Fonction pour démarrer le client MQTT (appelée depuis __init__.py)
def start_mqtt():
    client = mqtt.Client()  # Création du client MQTT
    client.on_connect = on_connect  # Assignation du callback de connexion
    client.on_message = on_message  # Assignation du callback de réception message

    try:
        # Connexion au broker MQTT
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()  # Démarre la boucle réseau en arrière-plan
        print(" MQTT client démarré.")
    except Exception as e:
        # En cas d'échec de connexion au broker MQTT
        print(f" Impossible de se connecter au broker MQTT : {e}")
