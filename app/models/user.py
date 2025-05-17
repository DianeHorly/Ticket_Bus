# app/models/user.py

from flask_login import UserMixin

# Cette classe représente un utilisateur connecté dans l'application.
# Elle hérite de UserMixin, qui fournit automatiquement les méthodes
# nécessaires pour que Flask-Login fonctionne correctement avec cette classe :
# - is_authenticated
# - is_active
# - is_anonymous
# - get_id()

class User(UserMixin):
    def __init__(self, id, name, email, password):
        # On stocke les infos de base de l'utilisateur :
        # - id : identifiant unique (généralement l'_id de MongoDB)
        # - name : nom affiché de l'utilisateur
        # - email : utilisé pour l'identification
        # - password : mot de passe (déjà hashé lorsqu'on l’utilise ici)
        self.id = id
        self.name = name
        self.email = email
        self.password = password

        # Flask-Login gère déjà ces attributs automatiquement via UserMixin :
        # self.is_authenticated = True
        # self.is_active = True

