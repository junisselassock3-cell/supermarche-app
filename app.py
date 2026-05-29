from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 🔴 CONFIG DATABASE (Render PostgreSQL)
database_url = "postgresql://supermarche_db_user:Gr10P9VOF2Y1uK2IiE6ddbCgwCDhDqfB@dpg-d7s077m7r5hc739lamrg-a.ohio-postgres.render.com/supermarche_db"

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])

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

# 🔴 CREATE TABLES
with app.app_context():
    db.create_all()

# 🔴 ROUTES
@app.route("/")
def home():
    return render_template("index.html")

# ➜ Ajouter produit
@app.route("/api/produits", methods=["POST"])
def ajouter_produit():
    data = request.get_json()

    nouveau = Produit(
        nom=data.get("nom"),
        prix=float(data.get("prix", 0)),
        stock=int(data.get("stock", 0))
    )

    db.session.add(nouveau)
    db.session.commit()

    return jsonify({"message": "Produit ajouté"})

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
def dashboard():
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