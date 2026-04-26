from flask import Flask, request, jsonify, render_template
from datetime import datetime
from flask_cors import CORS
import sqlite3
app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    return render_template("index.html")

# API ajouter produit
@app.route("/api/produits", methods=["POST"])
def ajouter_produit():
    data = request.get_json()
    print(data)
    nom = data.get("nom")
    prix = float(data.get("prix", 0))
    stock = int(data.get("stock") or 0)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produits (nom, prix, stock) VALUES (?, ?, ?)", (nom, prix, stock))
    conn.commit()
    conn.close()

    return jsonify({"message": "Produit ajouté"})

# API récupérer produits
@app.route("/api/produits", methods=["GET"])
def get_produits():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits ORDER BY id DESC")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    produits = []
    for rows in rows:
        produits.append(dict(zip(columns,rows)))
   
    conn.close()
    print(produits)
    return jsonify(produits)

@app.route("/api/produits/<int:id>", methods=["DELETE"])
def supprimer_produit(id):
    conn = get_db()
    conn.execute("DELETE FROM produits WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Produit supprimé"})

@app.route("/api/produits/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.json  # données envoyées en JSON
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produits
        SET nom = ?, prix = ?, stock = ?
        WHERE id = ?
    """, (data['nom'], data['prix'], data['stock'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Produit  mis à jour avec succès"})

@app.route("/api/produits/<int:id>/vendre", methods=["PUT"])
def acheter_produit(id):
    
    data = request.get_json()
    quantite = int(data.get("quantite", 0))
    conn = get_db()
    produit = conn.execute("SELECT * FROM produits WHERE id = ?", (id,)).fetchone()
    if not produit:
        conn.close()
        return jsonify({"message": "Produit non trouvé"}), 404

    if produit["stock"] < quantite:
        conn.close()
        return jsonify({"message": "Stock insuffisant"}), 400
    # Mettre à jour le stock
    conn.execute("UPDATE produits SET stock = stock - ? WHERE id = ?", (quantite, id))

    # Enregistrer la vente
    #conn.execute("INSERT INTO ventes (produit_id, quantite, total) VALUES (?, ?, ?)",
    #             (id, quantite, produit["prix"] * quantite))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Achat de {quantite} {produit['nom']} effectué"})


if __name__ == "__main__":
    app.run(debug=True)