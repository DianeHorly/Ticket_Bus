# app/routes/__init__.py

# J'importe les blueprints depuis leurs modules respectifs
from app.routes.auth import auth_bp
from app.routes.tickets import tickets_bp
from app.routes.dashboard import dashboard_bp

def register_blueprints(app):
    """
    Fonction pour enregistrer tous les blueprints sur l'application Flask.
    Cela permet de garder le fichier __init__.py principal propre et organisé.
    """
    app.register_blueprint(auth_bp)                         # Auth sans préfixe
    app.register_blueprint(tickets_bp, url_prefix="/tickets")  # Préfixe pour les routes de tickets
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")  # Préfixe pour le tableau de bord
