# run.py
# Ce script permet de lancer l'application Flask.
from app import create_app
from dotenv import load_dotenv
import logging

# Réduire les logs pymongo au minimum nécessaire
logging.getLogger("pymongo").setLevel(logging.WARNING)
load_dotenv()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)