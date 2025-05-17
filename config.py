# ticket_bus/config.py
import os  # Module pour accéder aux variables d'environnement

class Config:
    # Clé secrète utilisée par Flask pour sécuriser les sessions utilisateur
    # et protéger les formulaires contre les attaques CSRF.
    # Par défaut, une clé par défaut est fournie, mais il est recommandé
    # de définir la variable d'environnement SECRET_KEY en production.
    SECRET_KEY = os.getenv("SECRET_KEY", "une-cle-ultra-secrete-a-changer")

    # URI de connexion à MongoDB. 
    # Par défaut, elle pointe vers un conteneur Docker MongoDB nommé 'mongo' sur le port 27017.
    # En local, cette valeur peut être remplacée par une URI adaptée via la variable d'environnement MONGO_URI.
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

    # Nom de la base de données à utiliser (commenté ici car peut être fixé ailleurs)
    #DB_NAME = os.getenv("DB_NAME", "bus_app")

# Configuration spécifique à l'environnement de développement
class DevelopmentConfig(Config):
    # Active le mode debug de Flask (affichage des erreurs, rechargement automatique)
    DEBUG = True

    # Indique à Flask qu'on est en mode développement
    ENV = "development"