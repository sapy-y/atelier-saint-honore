
# Q9 - Detection des comportements atypiques
# Projet Data Mining - Atelier Saint-Honore

import pandas as pd
import matplotlib.pyplot as plt

from preparation import initialisation


# ============================================================
# 1. CHARGEMENT DES DONNEES
# ============================================================

df = initialisation()

print("=" * 60)
print("ANALYSE DES COMPORTEMENTS ATYPIQUES - Q9")
print("=" * 60)

print(f"\nNombre de clients analyses : {len(df)}")


# ============================================================
# 2. CALCUL DES SEUILS STATISTIQUES
# ============================================================

seuil_panier = df["panier_moyen_eur"].quantile(0.95)
seuil_montant = df["montant_euro"].quantile(0.95)
seuil_achats = df["nb_achats_12m"].quantile(0.95)

print("\nSEUILS DE DETECTION")
print(f"Panier moyen : {seuil_panier:.2f} euros")
print(f"Montant cumule : {seuil_montant:.2f} euros")
print(f"Nombre d'achats : {seuil_achats:.2f}")


# ============================================================
# 3. DETECTION DES ANOMALIES
# ============================================================

# Anomalies liees aux retours
df["anomalie_retours"] = (
    (df["retours"] >= 3)
    | (df["retours"] > df["nb_achats_12m"])
)

# Volumes d'achat particulierement eleves
df["volume_eleve"] = (
    (df["montant_euro"] >= seuil_montant)
    & (
        (df["panier_moyen_eur"] >= seuil_panier)
        | (df["nb_achats_12m"] >= seuil_achats)
    )
)

# Ratio de retours superieur a 50 %
df["ratio_retours_eleve"] = df["part_retours"] > 0.5

# Selection des clients presentant au moins un signal
clients_a_verifier = df[
    df["anomalie_retours"] | df["volume_eleve"]
].copy()


# ============================================================
# 4. CLASSIFICATION DES CLIENTS
# ============================================================

conditions = [
    (
        clients_a_verifier["anomalie_retours"]
        & clients_a_verifier["volume_eleve"]
    ),
    clients_a_verifier["anomalie_retours"],
    clients_a_verifier["volume_eleve"]
]

categories = [
    "Volume eleve et retours atypiques",
    "Retours atypiques",
    "Volume eleve"
]

clients_a_verifier["type_anomalie"] = [
    categories[0] if retour and volume
    else categories[1] if retour
    else categories[2]
    for retour, volume in zip(
        clients_a_verifier["anomalie_retours"],
        clients_a_verifier["volume_eleve"]
    )
]

# Priorite de verification
clients_a_verifier["priorite"] = [
    "Priorite elevee" if retour
    else "Controle du volume"
    for retour in clients_a_verifier["anomalie_retours"]
]


# ============================================================
# 5. EXPORT DES DOSSIERS A VERIFIER
# ============================================================

colonnes_export = [
    "client_id",
    "boutique_principale",
    "pays_residence",
    "anciennete_mois",
    "nb_achats_12m",
    "panier_moyen_eur",
    "montant_euro",
    "retours",
    "part_retours",
    "demandes_sav",
    "anomalie_retours",
    "volume_eleve",
    "ratio_retours_eleve",
    "type_anomalie",
    "priorite"
]

clients_a_verifier = clients_a_verifier.sort_values(
    ["anomalie_retours", "volume_eleve", "montant_euro"],
    ascending=[False, False, False]
)

clients_a_verifier[colonnes_export].to_csv(
    "q9_clients_a_verifier.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. SYNTHESE DES RESULTATS
# ============================================================

nombre_retours = int(df["anomalie_retours"].sum())
nombre_volumes = int(df["volume_eleve"].sum())
nombre_commun = int(
    (df["anomalie_retours"] & df["volume_eleve"]).sum()
)
nombre_total = len(clients_a_verifier)

bilan = pd.DataFrame({
    "indicateur": [
        "Clients analyses",
        "Anomalies liees aux retours",
        "Volumes d'achat eleves",
        "Clients dans les deux categories",
        "Total de clients distincts a verifier"
    ],
    "nombre": [
        len(df),
        nombre_retours,
        nombre_volumes,
        nombre_commun,
        nombre_total
    ]
})

bilan.to_csv(
    "q9_analyse_anomalies.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 60)
print("BILAN DE L'ANALYSE")
print("=" * 60)

print(bilan.to_string(index=False))

print(
    f"\nPart des clients a verifier : "
    f"{nombre_total / len(df) * 100:.2f} %"
)

print("\nREPARTITION DES ANOMALIES")

print(
    clients_a_verifier["type_anomalie"]
    .value_counts()
    .to_string()
)


# ============================================================
# 7. CREATION DU GRAPHIQUE
# ============================================================

repartition = clients_a_verifier["type_anomalie"].value_counts()

plt.figure(figsize=(10, 6))

barres = plt.bar(
    repartition.index,
    repartition.values
)

for barre in barres:
    hauteur = barre.get_height()
    plt.text(
        barre.get_x() + barre.get_width() / 2,
        hauteur,
        str(int(hauteur)),
        ha="center",
        va="bottom"
    )

plt.title("Repartition des clients presentant des anomalies")
plt.xlabel("Type d'anomalie")
plt.ylabel("Nombre de clients")
plt.xticks(rotation=10)
plt.tight_layout()

plt.savefig("q9_anomalies.png", dpi=300)

plt.show()


# ============================================================
# 8. CONFIRMATION
# ============================================================

print("\nFICHIERS GENERES :")
print("- q9_clients_a_verifier.csv")
print("- q9_analyse_anomalies.csv")
print("- q9_anomalies.png")

print("\nAnalyse Q9 terminee.")
