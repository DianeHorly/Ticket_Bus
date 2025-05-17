# ##############    app/tests/conftest.py          #########
# # cette partie de code est un fichier de configuration pour les tests
# # en utilisant pytest.   
import os
import pytest
import mongomock
from flask import session
from app import create_app
from app.models import user as user_model  
from bson import ObjectId

@pytest.fixture
def app(monkeypatch):
    # Utilisation d'une base Mongo mockée
    test_db = mongomock.MongoClient().db

    # Monkeypatch la fonction get_db pour qu'elle retourne la base mockée
    monkeypatch.setattr("app.routes.tickets.get_db", lambda: test_db)
    monkeypatch.setattr("app.routes.auth.get_db", lambda: test_db)
    monkeypatch.setattr("app.routes.dashboard.get_db", lambda: test_db)

    # Crée l'app Flask pour les tests
    app = create_app(test_config={
        "TESTING": True,
        "SECRET_KEY": "testkey",
        "WTF_CSRF_ENABLED": False,  # Pour ne pas bloquer les POST
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db(app):
    # Tu récupères ici la base mockée (déjà injectée dans l'app)
    return mongomock.MongoClient().db

# ===== Simuler l’authentification d’un utilisateur =====
class AuthActions:
    def __init__(self, client, db):
        self._client = client
        self._db = db
        self.user_id = None

    def login(self, username="diane", password="Diane1234"):
        user = {
            "_id": ObjectId(),
            "username": username,
            "password": password,
            "email": "diane@yahoo.com",
        }
        self.user_id = str(user["_id"])
        self._db["users"].insert_one(user)

        with self._client.session_transaction() as sess:
            sess["user_id"] = self.user_id

        return user

    def logout(self):
        with self._client.session_transaction() as sess:
            sess.clear()

@pytest.fixture
def auth(client, db):
    return AuthActions(client, db)
