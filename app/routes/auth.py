# app/routes/auth.py
# Ce script contient toutes les routes liées à l'authentification des utilisateurs :
# - inscription
# - connexion
# - déconnexion
# Il s'appuie sur Flask-Login, Flask-WTF et une base MongoDB.

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app.forms.auth_forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from app.models.user import User
from bson.objectid import ObjectId
from datetime import datetime, timedelta

# On crée un "blueprint", c’est un groupe de routes liées qu’on pourra enregistrer dans l’app principale
auth_bp = Blueprint('auth', __name__)

# === route vers la PAGE D’ACCUEIL ===
@auth_bp.route("/")
def index():
    # Affiche simplement la page d'accueil (landing page de l'app)
    return render_template("index.html")

# === Route vers la page d'INSCRIPTION ===
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()  # On instancie notre formulaire WTForms

    if form.validate_on_submit():  # Si le formulaire est bien rempli et soumis
        # Connexion à la base MongoDB (on récupère l’URI depuis la config Flask)
        mongo_client = MongoClient(current_app.config["MONGO_URI"])
        db = mongo_client["bus_app"]
        users = db["users"]

        # On vérifie si un utilisateur existe déjà avec cet email
        if users.find_one({"email": form.email.data}):
            flash("Cet email est déjà utilisé.", "danger")
        else:
            # Si l'email est unique : on hache le mot de passe pour plus de sécurité
            hashed_password = generate_password_hash(form.password.data)

            # On insère le nouvel utilisateur dans la base
            users.insert_one({
                "name": form.name.data,
                "email": form.email.data,
                "password": hashed_password
            })

            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("auth.login"))  # Redirige vers la page de login

    # Si on est en GET ou que le formulaire est invalide, on renvoie la page d'inscription
    return render_template("register.html", form=form)

# === Route vers la page de CONNEXION ===
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Si le formulaire est soumis et valide
        # On se connecte à la base et récupère l'utilisateur via l'email
        mongo_client = MongoClient(current_app.config["MONGO_URI"])
        db = mongo_client["bus_app"]
        users = db["users"]
        user_data = users.find_one({"email": form.email.data})

        if user_data:
            # Si l'utilisateur existe, on vérifie que le mot de passe correspond
            if check_password_hash(user_data["password"], form.password.data):
                # On crée un objet User (défini dans app/models/user.py) à partir des données MongoDB
                user_obj = User(
                    str(user_data["_id"]),
                    user_data["name"],
                    user_data["email"],
                    user_data["password"]
                )

                # On connecte l'utilisateur grâce à Flask-Login
                login_user(user_obj)

                flash("Bienvenue, connexion réussie !", "success")
                return redirect(url_for("tickets.buy_ticket"))  # Redirection après connexion réussie
            else:
                flash("Mot de passe incorrect.", "danger")
        else:
            flash("Email non trouvé.", "danger")

    # Si la requête est GET ou si une erreur est survenue, on affiche le formulaire
    return render_template("login.html", form=form)

# === route vers la page de DÉCONNEXION ===
@auth_bp.route("/logout")
@login_required  # Nécessite que l'utilisateur soit connecté
def logout():
    logout_user()  # Supprime l'utilisateur de la session
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))  # Retour vers la page de connexion
