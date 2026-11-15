import pandas as pd
from sklearn.linear_model import LinearRegression
from preparation import initialisation

df = initialisation()

# Recul = rapport_prochain (prochain achat / panier habituel) plus petit que 1.
# Presque tout le monde est sous 1, donc je compare la médiane du rapport entre les groupes.

# Touristes contre locaux
print("Touristes (1) contre locaux (0) :")
print(df.groupby("touriste")["rapport_prochain"].agg(["count", "median"]).round(3))
print(df.groupby("touriste")["recule"].mean().round(3))

# Les 3 canaux ("web" = canal "en ligne", "mixte" reste à part)
print("Les 3 canaux :")
print(df.groupby("canal_prefere")["rapport_prochain"].agg(["count", "median"]).round(3))
print(df.groupby("canal_prefere")["recule"].mean().round(3))

# On croise les deux pour voir lequel joue vraiment
print("Touriste et canal ensemble :")
print(df.groupby(["touriste", "canal_prefere"])["rapport_prochain"].agg(["count", "median"]).round(3))

# Où le panier recule-t-il ? (right=False : un client de 12 mois va dans la tranche 12-24)
df["tranche_anciennete"] = pd.cut(df["anciennete_mois"], [0, 12, 24, 48, 200], right=False)
print("Selon l'ancienneté :")
print(df.groupby("tranche_anciennete", observed=True)["rapport_prochain"].agg(["count", "median"]).round(3))

df["tranche_achats"] = pd.cut(df["nb_achats_12m"], [0, 3, 5, 9, 100], right=False)
print("Selon le nombre d'achats :")
print(df.groupby("tranche_achats", observed=True)["rapport_prochain"].agg(["count", "median"]).round(3))

print("Selon la carte de fidélité :")
print(df.groupby("carte_fidelite")["rapport_prochain"].agg(["count", "median"]).round(3))
print("Selon la ville de la boutique :")
print(df.groupby("ville")["rapport_prochain"].agg(["count", "median"]).round(3))

# Régression : les catégories deviennent des colonnes 0/1.
# Références : canal "boutique" et carte "aucune" (les 21 cartes "Inconnue" sont avec "aucune").
df["canal_en_ligne"] = (df["canal_prefere"] == "en ligne").astype(int)
df["canal_mixte"] = (df["canal_prefere"] == "mixte").astype(int)
df["carte_or"] = (df["carte_fidelite"] == "or").astype(int)
df["carte_argent"] = (df["carte_fidelite"] == "argent").astype(int)

# Pas de panier moyen ici : le rapport est calculé avec lui, le lien serait un effet du calcul.
colonnes_x = ["touriste", "canal_en_ligne", "canal_mixte", "anciennete_mois",
              "nb_achats_12m", "carte_or", "carte_argent"]
X = df[colonnes_x]
y = df["rapport_prochain"]

modele = LinearRegression()
modele.fit(X, y)

# Un coefficient = de combien le rapport change si la colonne augmente de 1, les autres restant pareils
resultat = pd.DataFrame({"colonne": colonnes_x, "coefficient": modele.coef_})
print(resultat.round(3))
print("R2 :", round(modele.score(X, y), 3))