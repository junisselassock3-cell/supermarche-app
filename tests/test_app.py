# --- Pages et connexion ---

def test_accueil_redirige_vers_login(client):
    r = client.get("/")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")


def test_page_login_accessible(client):
    assert client.get("/login").status_code == 200


def test_connexion_admin_reussie(client):
    r = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/dashboard")


def test_connexion_mauvais_mot_de_passe(client):
    r = client.post("/login", data={"username": "admin", "password": "faux"})
    assert r.status_code == 200  # on reste sur la page de login


# --- Produits ---

def test_ajout_produit_refuse_sans_connexion(client):
    r = client.post("/api/produits", json={"nom": "Riz", "prix": 1000, "stock": 10})
    assert r.status_code == 401


def test_ajout_et_liste_produit(admin_client):
    r = admin_client.post("/api/produits", json={"nom": "Huile", "prix": 2500, "stock": 4})
    assert r.status_code == 200

    produits = admin_client.get("/api/produits").get_json()
    assert len(produits) == 1
    assert produits[0]["nom"] == "Huile"
    assert produits[0]["stock"] == 4


def test_modifier_produit(admin_client, produit):
    r = admin_client.put(f"/api/produits/{produit}", json={"nom": "Riz parfumé", "prix": 1200, "stock": 8})
    assert r.status_code == 200
    assert admin_client.get("/api/produits").get_json()[0]["nom"] == "Riz parfumé"


def test_supprimer_produit(admin_client, produit):
    assert admin_client.delete(f"/api/produits/{produit}").status_code == 200
    assert admin_client.get("/api/produits").get_json() == []


def test_supprimer_produit_inexistant(admin_client):
    assert admin_client.delete("/api/produits/9999").status_code == 404


# --- Ventes ---

def test_vente_diminue_le_stock(admin_client, produit):
    r = admin_client.put(f"/api/produits/{produit}/vendre", json={"quantite": 3})
    assert r.status_code == 200
    assert admin_client.get("/api/produits").get_json()[0]["stock"] == 7

    ventes = admin_client.get("/api/ventes").get_json()
    assert len(ventes) == 1
    assert ventes[0]["total"] == 3000


def test_vente_stock_insuffisant(admin_client, produit):
    r = admin_client.put(f"/api/produits/{produit}/vendre", json={"quantite": 50})
    assert r.status_code == 400


# --- Tableau de bord ---

def test_dashboard_statistiques(admin_client, produit):
    admin_client.put(f"/api/produits/{produit}/vendre", json={"quantite": 7})
    stats = admin_client.get("/api/dashboard").get_json()
    assert stats["total_produits"] == 1
    assert stats["total_ventes"] == 1
    assert stats["chiffre_affaire"] == 7000
    assert stats["stock_faible"] == 1  # il reste 3 en stock, donc moins de 5
