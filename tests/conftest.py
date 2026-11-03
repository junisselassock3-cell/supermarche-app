import os
import sys

import pytest

# Base SQLite temporaire, séparée de la vraie base, fixée AVANT d'importer app.py
os.environ["DATABASE_URL"] = "sqlite:///test_supermarche.db"
os.environ["SECRET_KEY"] = "cle-de-test"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app, db, Produit, Vente  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
    # On vide les produits et les ventes entre deux tests (l'admin reste)
    with flask_app.app_context():
        Vente.query.delete()
        Produit.query.delete()
        db.session.commit()


@pytest.fixture
def admin_client(client):
    """Un client déjà connecté avec le compte admin créé au démarrage."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    return client


@pytest.fixture
def produit(admin_client):
    """Crée un produit 'Riz' (prix 1000, stock 10) et renvoie son id."""
    admin_client.post("/api/produits", json={"nom": "Riz", "prix": 1000, "stock": 10})
    return admin_client.get("/api/produits").get_json()[0]["id"]
