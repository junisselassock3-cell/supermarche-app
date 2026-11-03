from flask import Flask, request, jsonify, render_template, session,flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-a-changer")
CORS(app)

# 🔴 CONFIG DATABASE
# L'adresse de la base vient de la variable d'environnement DATABASE_URL.
# Par défaut (en local) : SQLite.
database_url = os.environ.get("DATABASE_URL", "sqlite:///supermarche.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Route vers les autres pages
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/produits")
def produits():
    produits = Produit.query.all()
    return render_template("produits.html", produits = produits)

@app.route("/ventes")
def ventes():
    ventes = Vente.query.all()
    return render_template("ventes.html", ventes = ventes)

@app.route("/login")
def login():
    
    return render_template("login.html")
@app.context_processor
def injet_admin():
    admin = None
    if "admin_id" in session:
        admin = Admin.query.get(session["admin_id"])
    return dict(admin=admin)

# 🔴 MODEL
class Produit(db.Model):
    __tablename__ = "produits"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    ventes = db.relationship("Vente", backref ="Produit", lazy =True)

class Vente(db.Model):
    __tablename__ ="ventes"
    id = db.Column(db.Integer, primary_key = True)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"),
                           nullable = False)
    quantite = db.Column(db.Integer,nullable = False)
    total = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime, default = db.func.current_timestamp())
class Admin(db.Model):
    __tablename__ ="admins"
    id = db.Column(db.Integer, primary_key =True)

    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
        

# 🔴 CREATE TABLES
with app.app_context():
    db.create_all()
    admin = Admin.query.filter_by(username = "admin").first()
    if not admin:
        hashed_password = generate_password_hash("admin123")
        new_admin = Admin(
            username = "admin", password = hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
        print("admin crée")

# 🔴 ROUTES
@app.route("/")
def home():
    return redirect("/login")

# ➜ Ajouter produit
@app.route("/api/produits", methods=["POST"])
def ajouter_produit():
    if "admin_id" not in session:
        return jsonify({"message": "Non autorisé"}), 401

    data = request.get_json()

    nouveau = Produit(
        nom=data.get("nom"),
        prix=float(data.get("prix", 0)),
        stock=int(data.get("stock", 0))
    )

    db.session.add(nouveau)
    db.session.commit()

    return jsonify({"message": "Produit ajouté"})
@app.route("/login", methods=[ "GET","POST"])
def m_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

    admin = Admin.query.filter_by(username=username).first()

    if not admin:
        flash( "Utilisateur introuvable"), 404
        return render_template("login.html")
    

    if not check_password_hash(admin.password, password):
        flash( "Mot de passe incorrect"), 401
        return render_template("login.html")

    session["admin_id"] = admin.id
    return redirect("/dashboard")

  # return jsonify({"message": "Connexion réussie"})
@app.route("/logout")
def logout():
    session.pop("admin_id", None)
    return redirect("/login")

# ➜ Récupérer produits
@app.route("/api/produits", methods=["GET"])
def get_produits():
    produits = Produit.query.order_by(Produit.id.desc()).all()

    result = []
    for p in produits:
        result.append({
            "id": p.id,
            "nom": p.nom,
            "prix": p.prix,
            "stock": p.stock
        })

    return jsonify(result)

# ➜ Supprimer
@app.route("/api/produits/<int:id>", methods=["DELETE"])
def supprimer_produit(id):
    produit = Produit.query.get(id)

    if not produit:
        return jsonify({"message": "Produit non trouvé"}), 404

    db.session.delete(produit)
    db.session.commit()

    return jsonify({"message": "Produit supprimé"})

# ➜ Modifier
@app.route("/api/produits/<int:id>", methods=["PUT"])
def update_produit(id):
    data = request.get_json()
    produit = Produit.query.get(id)

    if not produit:
        return jsonify({"message": "Produit non trouvé"}), 404

    produit.nom = data.get("nom")
    produit.prix = float(data.get("prix", 0))
    produit.stock = int(data.get("stock", 0))

    db.session.commit()

    return jsonify({"message": "Produit mis à jour"})


# ➜ Vendre produit
@app.route("/api/produits/<int:id>/vendre", methods=["PUT"])
def acheter_produit(id):
    data = request.get_json()
    quantite = int(data.get("quantite", 0))
    produit = Produit.query.get(id)
    if not produit:
        return jsonify({"message": "Produit non trouvé"}), 404

    if produit.stock < quantite:
        return jsonify({"message": "Stock insuffisant"}), 400

    produit.stock -= quantite
    vente = Vente(
         produit_id = produit.id,
        quantite = quantite,
        total = produit.prix * quantite
    )
    db.session.add(vente)
    db.session.commit()

    return jsonify({"message": f"Achat de {quantite} {produit.nom} effectué"})
@app.route("/api/ventes", methods=["GET"])
def get_ventes():

    ventes = Vente.query.order_by(Vente.id.desc()).all()

    result = []

    for vente in ventes:

        produit = Produit.query.get(vente.produit_id)

        result.append({
            "id": vente.id,
            "produit": produit.nom,
            "quantite": vente.quantite,
            "total": vente.total,
            "date": vente.date
        })

    return jsonify(result)
@app.route("/api/dashboard")
def api_dashboard():
    total_produits = Produit.query.count()

    ventes = Vente.query.all()

    total_ventes = Vente.query.count()

    chiffre_affaire = sum(v.total for v in ventes)

    stock_faible = Produit.query.filter(Produit.stock < 5).count()

    return jsonify({
        "total_produits": total_produits,
        "total_ventes": total_ventes,
        "chiffre_affaire": chiffre_affaire,
        "stock_faible": stock_faible
    })

@app.route("/api/stats/ventes")
def stats_ventes():

    ventes = Vente.query.all()

    data = {}

    for vente in ventes:

        produit = Produit.query.get(vente.produit_id)

        if produit.nom in data:
            data[produit.nom] += vente.quantite
        else:
            data[produit.nom] = vente.quantite

    return jsonify(data)

# 🔴 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)