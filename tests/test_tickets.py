##############    app/tests/test_tickets.py          #########
# cette partie de code est un test unitaire pour une application Flask
# qui gère l'achat et la validation de tickets de bus.
# Il utilise pytest pour exécuter les tests et pymongo pour interagir avec MongoDB.
# # Le test couvre plusieurs scénarios, y compris l'achat d'un ticket, la validation d'un ticket,
# l'annulation d'un ticket et la suppression d'un ticket expiré.    
# Il vérifie également que les réponses HTTP sont correctes et que les données dans la base de données sont mises à jour comme prévu.
###############

import pytest
from bson import ObjectId
from datetime import datetime, timedelta

# ==== Test : accès à la page d’achat de ticket ====
def test_get_buy_ticket_page(client, auth):
    auth.login()
    response = client.get("/buy")
    assert response.status_code == 200
    assert b"Type de ticket" in response.data

# ==== Test : achat d’un ticket valide (journalier) ====
def test_post_buy_ticket_journalier(client, auth, db):
    auth.login()
    response = client.post("/buy", data={
        "type": "journalier",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ticket achet" in response.data  # "acheté" est encodé en HTML

    # Vérifie que le ticket est bien en base
    ticket = db["tickets"].find_one()
    assert ticket is not None
    assert ticket["type"] == "journalier"
    assert ticket["valide"] is False
    assert "expiration" in ticket

# ==== Test : validation d’un ticket (journalier) ====
def test_valider_ticket(client, auth, db):
    auth.login()
    user_id = ObjectId(auth.user_id)

    # Insertion d’un faux ticket
    ticket_id = db["tickets"].insert_one({
        "user_id": user_id,
        "type": "journalier",
        "date_achat": datetime.utcnow(),
        "valide": False,
    }).inserted_id

    response = client.post(f"/valider/{ticket_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"valid" in response.data  # Vérifie que le message de validation est présent

    # Vérifie que le ticket a bien été mis à jour
    ticket = db["tickets"].find_one({"_id": ticket_id})
    assert ticket["valide"] is True
    assert "date_validation" in ticket
    assert "heure_expiration" in ticket

# ==== Test : annuler un ticket non validé ====
def test_annuler_ticket(client, auth, db):
    auth.login()
    user_id = ObjectId(auth.user_id)

    ticket_id = db["tickets"].insert_one({
        "user_id": user_id,
        "type": "journalier",
        "valide": False,
        "date_achat": datetime.utcnow()
    }).inserted_id

    response = client.post(f"/annuler/{ticket_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"annul" in response.data  # Message d'annulation attendu

    # Vérifie que le ticket a été supprimé
    assert db["tickets"].find_one({"_id": ticket_id}) is None

# ==== Test : suppression d’un ticket expiré ====
def test_supprimer_ticket_expire(client, auth, db):
    auth.login()
    user_id = ObjectId(auth.user_id)

    ticket_id = db["tickets"].insert_one({
        "user_id": user_id,
        "type": "journalier",
        "valide": True,
        "expiré": True,
        "heure_expiration": datetime.utcnow() - timedelta(days=1),
        "date_achat": datetime.utcnow() - timedelta(days=2),
    }).inserted_id

    response = client.post(f"/supprimer/{ticket_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"supprim" in response.data

    # Vérifie que le ticket a été supprimé
    assert db["tickets"].find_one({"_id": ticket_id}) is None
