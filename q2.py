import pandas as pd
from preparation import initialisation

df = initialisation()

# On veut que "revient" vaille 1 quand le client est revenu, 0 sinon.
df["revenu"] = (df["depart"] == 0).astype(int) 
print(df["revenu"].sum())    # 288
print(len(df["revenu"]))     # 700

# Morceau B : corrélation de ces colonnes avec "revenu"
colonnes = ["anciennete_mois", "nb_achats_12m", "panier_moyen_eur", "montant_euro", "revenu"]
print(df[colonnes].corr().round(2))

# Morceau C : montant moyen et médian des clients revenus et non revenus
print(df.groupby("revenu")["montant_euro"].agg(["count", "mean", "median"]))

# Morceau D : 4 tranches de montant à effectifs égaux (quartiles)
df["tranche_montant"] = pd.qcut(df["montant_euro"], 4, labels=["bas", "moyen-bas", "moyen-haut", "haut"])

# Taux de retour par tranche : la moyenne de revenu (0/1) est la part de clients revenus
print(df.groupby("tranche_montant", observed=True)["revenu"].agg(["count", "mean"]))

# Morceau E : les clients mal classés par le montant
haut_non_revenu = (df["tranche_montant"] == "haut") & (df["revenu"] == 0 )
bas_revenu = (df["tranche_montant"] == "bas" ) & (df["revenu"] == 1 )

print("haut et non revenus :", haut_non_revenu.sum())
print("bas et revenus :", bas_revenu.sum())
print("total mal classés :", haut_non_revenu.sum() + bas_revenu.sum())
