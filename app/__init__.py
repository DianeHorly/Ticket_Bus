# app/__init__.py

# === Import des bibliothèques nécessaires ===
from flask import Flask, render_template, current_app
from flask_wtf.csrf import CSRFProtect  # Protection contre les attaques sur les formulaires
from flask_login import LoginManager   # Pour gérer les connexions utilisateur
from pymongo import MongoClient        # Connexion à MongoDB
from bson.objectid import ObjectId     # Pour manipuler les IDs Mongo
import os
from config import DevelopmentConfig             # Configuration centralisée dans un fichier dédié

# === Connexion à MongoDB ===
# On établit ici la connexion à la base de données MongoDB.
# L'URI est récupérée via une variable d'environnement (utile pour la prod), ou une valeur par défaut sinon.
client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["bus_app"]  # Nom de la base de données utilisée dans cette application

# Import du modèle utilisateur (défini dans models/user.py)
from app.models.user import User

# === Initialisation des modules Flask ===
csrf = CSRFProtect()        # Active la protection CSRF sur les formulaires
login_manager = LoginManager()  # Gère les sessions utilisateur (connexion/déconnexion)

# === Fonction principale qui crée l'application Flask ===
def create_app():
    # Création de l’instance Flask
    app = Flask(__name__)

    # Chargement des paramètres depuis le fichier config.py
    app.config.from_object(DevelopmentConfig)

    # Initialisation de CSRF et Flask-Login avec l'app Flask
    csrf.init_app(app)
    login_manager.init_app(app)

    # Si un utilisateur non connecté tente d’accéder à une page protégée, il sera redirigé ici
    login_manager.login_view = "auth.login"

    # === Définition de la fonction de chargement d’un utilisateur connecté ===
    # Flask-Login a besoin d’une fonction pour "recharger" l'utilisateur à partir de son ID (stocké en session)
    @login_manager.user_loader
    def load_user(user_id):
        # On va chercher l’utilisateur dans MongoDB grâce à son ID
        user_data = db["users"].find_one({"_id": ObjectId(user_id)})

        # Si l’utilisateur est trouvé, on le convertit en objet User (défini dans le modèle)
        if user_data:
            return User(
                str(user_data["_id"]),
                user_data["name"],
                user_data["email"],
                user_data["password"]
            )

        # Si l'utilisateur n'existe plus (ou ID invalide), on retourne None
        return None

    # === Enregistrement des routes de l’application ===
    # Cette fonction va attacher les différents "blueprints" (groupes de routes) à l'application
    from app.routes import register_blueprints
    register_blueprints(app)

    # === Gestion personnalisée des erreurs ===

    # Erreur 404 : page non trouvée
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error.html", message="La page que vous cherchez est introuvable."), 404

    # Erreur 500 : erreur interne du serveur (ex : plantage du code)
    @app.errorhandler(500)
    def internal_server_error(error):
        current_app.logger.error(f"Erreur 500 : {error}")  # On log l’erreur pour pouvoir l’analyser plus tard
        return render_template("error.html", message="Une erreur interne est survenue. Veuillez réessayer plus tard."), 500

    # Toute autre erreur non prévue (Exception générale)
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        current_app.logger.exception("Une erreur inattendue s'est produite.")
        return render_template("error.html", message="Quelque chose s'est mal passé. Nous investiguons..."), 500

    # === Intégration du client MQTT (optionnel) ===
    # Si l’application utilise des messages temps réel via MQTT, on démarre le client ici
    from app.mqtt_client import start_mqtt
    start_mqtt()

    # === Lancement final ===
    # On retourne l’objet Flask prêt à être lancé
    return app
