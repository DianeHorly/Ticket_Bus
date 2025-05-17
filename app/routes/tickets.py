# app/routes/tickets.py
# Ce module contient toutes les routes qui permettent à un utilisateur d’acheter, valider,
# consulter ou annuler un ticket de bus.

#========== Importations des modules nécessaires ==========
# On importe les modules Flask, MongoDB, et d'autres utilitaires nécessaires
from flask import render_template, redirect, url_for, flash, current_app, request, Blueprint
from flask_login import login_required, current_user
from app.forms.ticket_forms import BuyTicketForm
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pymongo import MongoClient
import qrcode, os
from app import csrf
import logging

# Active les logs pour faciliter le débogage
logging.basicConfig(level=logging.DEBUG)

# Création du blueprint pour le groupe de routes "tickets"
tickets_bp = Blueprint('tickets', __name__)

# =============  Route pour acheter un ticket  ==============================
@tickets_bp.route("/buy", methods=["GET", "POST"])
@login_required  # Seuls les utilisateurs connectés peuvent acheter un ticket
def buy_ticket():
    form = BuyTicketForm()  # Formulaire pour sélectionner le type de ticket

    if form.validate_on_submit():
        ticket_type = form.type.data

        # Contrôle manuel du champ validity_days pour certains types
         # Vérification pour ticket personnalisé
        if ticket_type == "personnalisé":
            validity_days = form.validity_days.data
            if not validity_days or not (1 <= validity_days <= 365):
                flash("Veuillez choisir une durée entre 1 et 365 jours.", "danger")
                return render_template("buy_ticket.html", form=form)
        
        # Connexion à la base MongoDB
        mongo_client = MongoClient(current_app.config["MONGO_URI"])
        db = mongo_client["bus_app"]
        tickets = db["tickets"]

        # Génération d’un QR code unique contenant l’ID utilisateur + horodatage
        ticket_data = f"{current_user.id}_{datetime.utcnow().isoformat()}"
        qr_img = qrcode.make(ticket_data)

        # Construction du chemin et nom du fichier à sauvegarder
        filename = f"qr_{current_user.id}_{datetime.utcnow().timestamp()}.png"
        qr_path = os.path.join("app", "static", "qr_codes", filename)

        # Création du dossier "qr_codes" s’il n’existe pas encore
        qr_dir = os.path.dirname(qr_path)
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)

        # Sauvegarde de l’image du QR code sur le serveur
        qr_img.save(qr_path)

        # Enregistrement des infos du ticket dans MongoDB
        date_achat = datetime.utcnow()
        expiration = None

        # Définir une date d'expiration uniquement pour les tickets 
        if ticket_type == "horaire":
            expiration = date_achat + timedelta(hours=1)           
        elif ticket_type == "semaine":
            expiration = date_achat + timedelta(days=7)
        elif ticket_type == "mensuel":
            expiration = date_achat + timedelta(days=30)
        elif ticket_type == "annuel":
            expiration = date_achat + timedelta(days=365)
        elif ticket_type == "journalier":
            # Pour les types comme "journalier", on peut fixer 1 jour ou ignorer expiration
            expiration = date_achat + timedelta(days=1)
        elif ticket_type == "personnalisé":
            pass
            

        # Structure du ticket à insérer
        # Construction du ticket sans qr_code_path pour l'instant
        new_ticket = {
            "user_id": ObjectId(current_user.id),
            "type": ticket_type,
            #"qr_code_path": f"static/qr_codes/{filename}",
            "date_achat": date_achat,
            "valide": False  # Par défaut, le ticket n'est pas encore validé
        }

        # Ajout de l’expiration seulement si elle a été calculée
        if expiration:
            new_ticket["expiration"] = expiration

         # Ajoute validity_days (la durée) uniquement pour les tickets personnalisés
        if ticket_type == "personnalisé":
            new_ticket["validity_days"] = validity_days

       # Insertion en base de données
       # Insertion du ticket (sans qr_code_path)
        result = tickets.insert_one(new_ticket)
        ticket_id = result.inserted_id
        
        """
        # Génération QR code avec l’ID MongoDB du ticket (sous forme string)
        qr_data = str(ticket_id)
        qr_img = qrcode.make(qr_data)

        # Préparer le chemin du QR code
        filename = f"qr_{ticket_id}.png"
        qr_dir = os.path.join("app", "static", "qr_codes")
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
        qr_path = os.path.join(qr_dir, filename)

        qr_img.save(qr_path)
"""
        # Mettre à jour le ticket avec le chemin du QR code
        tickets.update_one(
            {"_id": ticket_id},
            {"$set": {"qr_code_path": f"static/qr_codes/{filename}"}}
        )

       
        flash("Ticket acheté avec succès !", "success")
        return redirect(url_for("dashboard.dashboard"))

    # Affiche le formulaire si on arrive sur la page en GET ou si erreur
    return render_template("buy_ticket.html", form=form)

# ============  Route pour consulter tous ses tickets  ================
@tickets_bp.route("/mes-tickets")
@login_required
def my_tickets():
    mongo_client = MongoClient(current_app.config["MONGO_URI"])
    db = mongo_client["bus_app"]
    # On récupère tous les tickets liés à l’utilisateur courant
    #tickets = db["tickets"].find({"user_id": current_user.id})
    #return render_template("my_tickets.html", tickets=tickets)
    user_id = ObjectId(current_user.id)
    #tickets_cursor = db["tickets"].find({"user_id": user_id})
  
    now = datetime.utcnow()
    
    # Récupération des tickets
    tickets_cursor = db["tickets"].find({"user_id": user_id})
    tickets = []
    
    for t in tickets_cursor:
        # Par défaut : le ticket n'est pas expiré
        t["expiré"] = False
        
        # Si le ticket est validé, on vérifie l’expiration
        if t.get("valide") and t.get("expiration") and datetime.utcnow() > t["expiration"]:
            expiration = t.get("heure_expiration")
            if expiration and now > expiration:
                t["expiré"] = True
        tickets.append(t)

    return render_template("my_tickets.html", tickets=tickets)
    


# ==========  Route pour valider un ticket  =========================
@tickets_bp.route("/valider/<ticket_id>", methods=["POST"])
@login_required
def valider_ticket(ticket_id):
    mongo_client = MongoClient(current_app.config["MONGO_URI"])
    db = mongo_client["bus_app"]
    tickets_collection = db["tickets"]

    try:
        # Conversion sécurisée des IDs pour MongoDB
        ticket_object_id = ObjectId(ticket_id)
        user_object_id = ObjectId(current_user.id)
    except Exception as e:
        flash("ID de ticket invalide.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    # Vérifie que le ticket appartient bien à l'utilisateur connecté
    ticket = tickets_collection.find_one({"_id": ticket_object_id , "user_id": user_object_id})

    if not ticket:
        flash("Ticket introuvable ou accès non autorisé.", "danger")
        return redirect(url_for("dashboard.dashboard"))

   # Empêche la validation de tickets déjà valides ou expirés
    if ticket.get("valide"):
        flash("Ce ticket est déjà validé.", "info")
        return redirect(url_for("dashboard.dashboard"))

    if ticket.get("expiration") and datetime.utcnow() > ticket["expiration"]:
        flash("Ce ticket est expiré.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Cas particulier : ticket horaire déjà expiré
    if ticket["type"] == "horaire" and ticket.get("expiration") and datetime.utcnow() > ticket["expiration"]:
        flash("Ce ticket horaire est déjà expiré.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Heure de validation actuelle (UTC)
    now = datetime.utcnow()

    # Calcul dynamique de la durée de validité
    type_ticket = ticket.get("type", "").lower()
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
    elif type_ticket == "personnalisé":
        jours = ticket.get("validity_days", 0)
        if not isinstance(jours, int) or not (1 <= jours <= 365):
            flash("Durée personnalisée invalide.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        validité = timedelta(days=jours)
    else:
        flash("Type de ticket inconnu.", "danger")
        return redirect(url_for("dashboard.dashboard"))


    # Date d’expiration calculée
    #expiration = now + validité
    date_validation = datetime.utcnow()
    d_expiration = date_validation + validité

    # Mise à jour du ticket : valide, heure de validation et expiration
    tickets_collection.update_one(
        {"_id": ticket_object_id},
        {
            "$set": {
                "valide": True,
                #"heure_validation": now,
                "heure_expiration": d_expiration,
                "date_validation": date_validation,
            }
        }
    )

    flash("Ticket validé avec succès !", "success")
    return redirect(url_for("dashboard.dashboard"))


# =========  Route pour annuler un ticket  ==========================
@tickets_bp.route("/annuler/<ticket_id>", methods=["POST"])
@login_required
def annuler_ticket(ticket_id):
    mongo_client = MongoClient(current_app.config["MONGO_URI"])
    db = mongo_client["bus_app"]
    tickets_collection = db["tickets"]

    try:
        # Conversion sécurisée des IDs
        ticket_object_id = ObjectId(ticket_id)
        user_object_id = ObjectId(current_user.id)
    except Exception:
        flash("ID de ticket invalide.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Vérifie que le ticket existe bien et appartient à l'utilisateur
    ticket = tickets_collection.find_one({"_id": ticket_object_id, "user_id": user_object_id})

    if not ticket:
        flash("Ticket introuvable ou accès non autorisé.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # On ne peut pas annuler un ticket qui a déjà été utilisé/validé
    if ticket.get("valide", False):
        flash("Impossible d’annuler un ticket déjà validé.", "warning")
    else:
        tickets_collection.delete_one({"_id": ticket_object_id})
        flash("Ticket annulé avec succès.", "success")

    return redirect(url_for("dashboard.dashboard"))


# ==========  Route pour supprimer un ticket expiré  ==========================
@tickets_bp.route("/supprimer/<ticket_id>", methods=["POST"])
@login_required
def supprimer_ticket(ticket_id):
    mongo_client = MongoClient(current_app.config["MONGO_URI"])
    db = mongo_client["bus_app"]
    tickets_collection = db["tickets"]

    try:
        ticket_object_id = ObjectId(ticket_id)
        user_object_id = ObjectId(current_user.id)
    except Exception:
        flash("ID de ticket invalide.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    ticket = tickets_collection.find_one({"_id": ticket_object_id, "user_id": user_object_id})

    if not ticket:
        flash("Ticket introuvable ou accès non autorisé.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if not ticket.get("expiré"):
        flash("Seuls les tickets expirés peuvent être supprimés.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    # Supprimer le ticket de la base de données
    tickets_collection.delete_one({"_id": ticket_object_id})
    flash("Ticket expiré supprimé avec succès.", "success")
    return redirect(url_for("dashboard.dashboard"))
