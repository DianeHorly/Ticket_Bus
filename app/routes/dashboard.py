# app/routes/dashboard.py
# Ce module gère l'affichage du tableau de bord utilisateur.
# Il affiche les tickets achetés et vérifie leur statut (valide ou expiré).

#==========    Importations   =============================
# On importe les modules nécessaires pour le fonctionnement de cette partie de l'application
from flask import Blueprint, render_template, current_app, flash
from flask_login import login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from app.forms.ticket_forms import ValidationTicketForm

# ============  Déclaration du blueprint   ===============
# Ce blueprint regroupe toutes les routes liées au tableau de bord utilisateur
dashboard_bp = Blueprint('dashboard', __name__)

# ============   Route principale du tableau de bord  =================
@dashboard_bp.route("/")
@login_required  # On ne peut y accéder que si on est connecté
def dashboard():
    try:
        # Connexion à MongoDB via les paramètres de config de l'app Flask
        mongo_client = MongoClient(current_app.config["MONGO_URI"])
        db = mongo_client["bus_app"]
        tickets_collection = db["tickets"]

        # Conversion de l'ID utilisateur depuis Flask-Login en ObjectId pour Mongo
        try:
            user_object_id = ObjectId(current_user.id)
        except Exception as e:
            flash("Erreur de format d'identifiant utilisateur.", "danger")
            return render_template("dashboard.html", tickets=[], current_year=datetime.now().year)

        # On récupère tous les tickets achetés par cet utilisateur
        tickets = list(tickets_collection.find({"user_id": user_object_id}))

        # === Vérification des dates d’expiration des tickets ===
        for ticket in tickets:
            type_ticket = ticket.get("type", "").lower()
            date_achat = ticket.get("date_achat", datetime.utcnow())

            # Définition de la durée de validité en fonction du type de ticket
            if type_ticket == "horaire":
                validité = timedelta(hours=1)
            elif type_ticket == "journalier":
                validité = timedelta(days=1)
            elif type_ticket == "semaine":
                validité = timedelta(weeks=1)
            elif type_ticket == "mensuel":
                validité = timedelta(days=30)
            elif type_ticket == "annuel":
                validité = timedelta(days=365)
            else:
                # Si le type est inconnu, on considère le ticket comme déjà expiré
                validité = timedelta(days=ticket.get("validity_days", 0) or 0)

            # Calcul si: le ticket est-il expiré ?
            est_expiré = datetime.utcnow() > date_achat + validité

           # Si le ticket est validé et possède une heure d'expiration enregistrée
            if ticket.get("valide") and ticket.get("heure_expiration"):
                try:
                    heure_expiration = ticket["heure_expiration"]
                    if isinstance(heure_expiration, str):
                        heure_expiration = datetime.strptime(heure_expiration, "%Y-%m-%d %H:%M:%S")

                    est_expiré = datetime.utcnow() > heure_expiration
                except Exception as e:
                    print(f"Erreur de parsing d'heure_expiration pour ticket {ticket['_id']}: {e}")
                    est_expiré = False
            else:
                # Fallback : calcul basé sur la date d'achat + validité
                est_expiré = datetime.utcnow() > date_achat + validité

            # Mise à jour en base et locale si expiration détectée
            if est_expiré and not ticket.get("expiré", False):
                tickets_collection.update_one(
                    {"_id": ticket["_id"]},
                    {"$set": {"expiré": True, "valide": False}}
                )
                ticket["expiré"] = True
                ticket["valide"] = False
            else:
                ticket["expiré"] = est_expiré
                # On recharge la liste des tickets depuis MongoDB pour refléter les mises à jour
                tickets = list(tickets_collection.find({"user_id": user_object_id}))

        # Création d’un formulaire de validation pour chaque ticket affiché
        forms = {str(ticket["_id"]): ValidationTicketForm() for ticket in tickets}

        # On affiche le tableau de bord avec les tickets et les formulaires associés
        return render_template("dashboard.html", tickets=tickets, forms=forms, current_year=datetime.now().year)

    except Exception as e:
        # En cas d'erreur inattendue, on affiche un message à l'utilisateur
        flash("Une erreur est survenue lors du chargement du tableau de bord.", "danger")
        print("Erreur dans dashboard():", e)
        return render_template("dashboard.html", tickets=[], forms={}, current_year=datetime.now().year)
