# app/forms/ticket_forms.py

#==========    Imports nécessaires  ====================
# On importe les modules nécessaires pour créer des formulaires web avec Flask-WTF
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

# =======   Formulaire d'achat de ticket  ============
# Ce formulaire permet à l'utilisateur de choisir le type de ticket
# ainsi que la durée de validité (en jours) pour certains tickets.
class BuyTicketForm(FlaskForm):
    # Liste déroulante pour choisir le type de ticket
    # Chaque option affiche le nom du ticket et son prix.
    type = SelectField(
        'Type de ticket',
        choices=[
            ('horaire', 'Horaire durée 1h (1.80€)'),
            ('journalier', 'Journalier (5€)'),
            ('semaine', 'Hebdomadaire (20€)'),
            ('mensuel', 'Mensuel (70€)'),
            ('annuel', 'Annuel (300€)'),
            ('personnalisé', 'Personnalisé'),
        ],
        validators=[DataRequired()]  # Le choix est obligatoire
    )

    # Champ pour définir la validité en jours (uniquement pour certains types de tickets)
    # La valeur doit être comprise entre 1 et 30 jours.
    validity_days = IntegerField(
        'Validité (en jours)',
        validators=[
            Optional(),                
            NumberRange(min=1, max=365, message="Veuillez entrer un nombre entre 1 et 365.")    # Valeur selon le type de ticket
            
        ],
        default=1,  # Valeur par défaut
        render_kw={"placeholder": "Durée de validité (en jours)"}  # Placeholder pour le champ
    )

    # Bouton pour soumettre le formulaire et acheter le ticket
    submit = SubmitField('Acheter le ticket')


# ========  Formulaire pour valider un ticket  =========
# Simple formulaire avec un bouton pour confirmer la validation du ticket.
class ValidationTicketForm(FlaskForm):
    submit = SubmitField('Valider')
