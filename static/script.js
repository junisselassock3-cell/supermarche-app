console.log("script charg");   
let currentId = null;
let currentModal = null;

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM pret");
    const btn = document.getElementById("addBtn");
    const modal = document.getElementById("modalContainer");
    const actionBtn = document.getElementById("modalActionBtn");
    document.getElementById("cancelBtn").addEventListener("click", closeModal);

    console.log("Bouton =", btn);
    console.log("Modale =", modal);
    console.log("MODALEB=", actionBtn)
    console.log(document.getElementById("modalActionBtn"))
    
    if(btn){
        btn.addEventListener("click", () => {
             console.log("Clik ok");
             openModal("add");
        
       } );
    } else {
        console.log("Bouton non trouvé");  
    }
    
});

  

// Nouvelle version de openModal pour edit/sell
function openModal(type, id = null){
    const modal = document.getElementById("modalContainer");
    const title = document.getElementById("modalTitle");
        body = document.getElementById("modalBody");
    const actionBtn = document.getElementById("modalActionBtn")
    console.log("type = ", type);

    currentModal = type;
    currentId = id;
    modal.classList.remove("hidden");

    ;
    body.innerHTML = "";
    if (type === "add") {
        title.textContent = "Ajouter un produit";
        body.innerHTML = `
        
            <input id="nom" placeholder="Nom" class="w-full border px-2 py-1 rounded">
            <input id="prix" type="number" placeholder="Prix" class="w-full border px-2 py-1 rounded">
            <input id="stock" type="number" placeholder="Stock" class="w-full border px-2 py-1 rounded">
             `;
       actionBtn.onclick = ajouterProduit
    } else if (type === "edit") {
        // Récupérer le produit depuis le tableau déjà chargé
        const produit = produitsData.find(p => p.id === id);
        title.textContent = "Modifier le produit";
        body.innerHTML = `
            <input id="nom" value="${produit.nom}" class="w-full border px-2 py-1 rounded">
            <input id="prix" type="number" value="${produit.prix}" class="w-full border px-2 py-1 rounded">
            <input id="stock" type="number" value="${produit.stock}" class="w-full border px-2 py-1 rounded">
        `;
        actionBtn.onclick = modifierProduit;
    } else if (type === "sell") {
        const produit = produitsData.find(p => p.id === id);
        title.textContent = `Vendre le produit: ${produit.nom}`;
        body.innerHTML = `
            <input id="quantite" type="number" placeholder="Quantité" value="1" class="w-full border px-2 py-1 rounded">
        `;
        actionBtn.onclick = vendreProduit;
    }
    else if (type === "delete"){
         const produit = produitsData.find(p => p.id === id);
        title.textContent = "Supprimer le produit";
        body.innerHTML = `
            <input id="nom" value="${produit.nom}" class="w-full border px-2 py-1 rounded">
            <input id="prix" type="number" value="${produit.prix}" class="w-full border px-2 py-1 rounded">
            <input id="stock" type="number" value="${produit.stock}" class="w-full border px-2 py-1 rounded">
        `;
        actionBtn.onclick = () => supprimerProduit(currentId);

    }
}

// Stocker les produits pour réutilisation
let produitsData = [];

async function fetchProduits() {
    const res = await fetch("/api/produits");
    produitsData = await res.json(); // sauvegarde
    console.table(produitsData);
    const tbody = document.getElementById("tableProduits");
    tbody.innerHTML = "";
    produitsData.forEach(p => {
        tbody.innerHTML += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-2">${p.id}</td>
                <td class="px-6 py-2">${p.nom}</td>
                <td class="px-6 py-2">${p.prix} F</td>
                <td class="px-6 py-2">${p.stock}</td>
                <td class="px-6 py-2 space-x-1">
                    <button class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded" onclick='openModal("edit", ${p.id})'>Modifier</button>
                    <button class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded" onclick="supprimerProduit( ${p.id})">Supprimer</button>
                    <button class="bg-yellow-400 hover:bg-yellow-500 text-white px-2 py-1 rounded" onclick='openModal("sell", ${p.id})'>Vendre</button>
                </td>
            </tr>
        `;
    });
}
function ajouterProduit() {
    console.log("CLICK DETECTE");
    const nom = document.getElementById("nom").value;
    const prix = document.getElementById("prix").value;
    const stock = document.getElementById("stock").value;

    fetch("/api/produits", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ nom: nom, prix: prix, stock: stock })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
       fetchProduits();
        closeModal()
    });
}
function closeModal() {
    const modal = document.getElementById("modalContainer");
    modal.classList.add("hidden");
    const body = document.getElementById("modalBody");
    if (body) body.innerHTML = "";
}
async function supprimerProduit(id) {
     console.log("CLICK DETECTE");
    if (!confirm("Tu veux vraiment supprimer ce produit ?")) return;

    await fetch(`/api/produits/${id}`, {
        method: "DELETE"
    });

    await fetchProduits();
}
async function modifierProduit() {
     console.log("CLICK DETECTE");
    const id = currentId;

    const nom = document.getElementById("nom").value;
    const prix = document.getElementById("prix").value;
    const stock = document.getElementById("stock").value;

    const response = await fetch(`/api/produits/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nom: nom,
            prix: prix,
            stock: stock
        })
    });

    const data = await response.json();
    alert(data.message);

    await fetchProduits(); // refresh tableau
    closeModal();
}

async function vendreProduit() {
    try {
        console.log("VENTE CLICK");
        console.log("METHODE = PUT")

        const id = currentId;
        const quantite = document.getElementById("quantite").value;

        console.log("ID =", id);
        console.log("Quantité =", quantite);

        if (!quantite || quantite <= 0) {
            alert("Quantité invalide");
            return;
        }

        console.log("ENVOI FETCH...");

        const response = await fetch(`/api/produits/${id}/vendre`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ quantite })
        });

        console.log("FETCH OK");

        const data = await response.json();
        console.log("DATA =", data);

        alert(data.message);

        await fetchProduits();
        closeModal();

    } catch (error) {
        console.error("ERREUR JS :", error);
    }
}