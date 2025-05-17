# app/forms/auth_forms.py

#==========    Imports nécessaires  ====================
# On importe les modules nécessaires pour créer des formulaires web avec Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# =========    Formulaire d'inscription  ====================
# Ce formulaire est affiché sur la page de création de compte.
# Il permet à un nouvel utilisateur de saisir son nom, son adresse email et un mot de passe sécurisé.
class RegistrationForm(FlaskForm):
    # Champ pour le nom complet de l'utilisateur
    name = StringField("Nom complet", validators=[DataRequired()])

    # Champ pour l'adresse email (doit être une adresse valide)
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Champ pour le mot de passe :
    # -> Doit contenir au minimum 6 caractères
    password = PasswordField("Mot de passe", validators=[
        DataRequired(),
        Length(min=6, message="Le mot de passe doit faire au moins 6 caractères")
    ])

    # Confirmation du mot de passe :
    # -> Doit être identique au champ "password"
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[
        DataRequired(),
        EqualTo("password", message="Les mots de passe doivent correspondre.")
    ])

    # Bouton de soumission du formulaire
    submit = SubmitField("S'inscrire")


# ========    Formulaire de connexion   =======================
# Ce formulaire permet aux utilisateurs existants de se connecter.
# Il demande uniquement l'email et le mot de passe.
class LoginForm(FlaskForm):
    # Email de l'utilisateur (doit être une adresse email valide)
    email = StringField('Email', validators=[DataRequired(), Email()])

    # Mot de passe associé à l'adresse email
    password = PasswordField('Mot de passe', validators=[DataRequired()])

    # Bouton de soumission du formulaire
    submit = SubmitField('Se connecter')
