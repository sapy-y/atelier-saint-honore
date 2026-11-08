import pandas as pd

def initialisation ():
    df = pd.read_csv("SaintHonore_clients.csv")
    df = df.drop_duplicates()
#harmonisation des colones montant 
    df["montant_euro"] = df["montant_total_centimes"] / 100
    df = df.drop(columns=["montant_total_centimes"])
#verification des incohérences sur la colonne panier_moyen_eur
    panier_impossible = df["panier_moyen_eur"].isna() | (df["panier_moyen_eur"] <= 0 ) 
    df.loc[panier_impossible , "panier_moyen_eur"] = df["montant_euro"] / df["nb_achats_12m"]
#verification des incohérences sur la colonne nb_achats_12m
    nb_achats_impossible = df["nb_achats_12m"].isna() | (df["nb_achats_12m"] <= 0) 
    df.loc[nb_achats_impossible , "nb_achats_12m"] = df["montant_euro"] / df["panier_moyen_eur"]
# remplacement des valeurs manquantes
    df["carte_fidelite"] = df["carte_fidelite"].fillna("Inconnue")
    df["canal_prefere"] = df["canal_prefere"].fillna("Inconnu")
    df["pays_residence"] = df["pays_residence"].fillna("Inconnu")
    df["est_revenu_6m"] = df["est_revenu_6m"].fillna("Inconnu")

    return df

if __name__ == "__main__":
    nt_client = initialisation()
    pd.set_option("display.float_format", "{:.2f}".format)
    print(nt_client.shape)
    print(nt_client.head())
    print(nt_client.describe().T)
    print(nt_client.isna().sum())
    print(nt_client.duplicated().sum())
    print(nt_client["carte_fidelite"].value_counts(dropna=False))
    print(nt_client["canal_prefere"].value_counts(dropna=False))
    print(nt_client["pays_residence"].value_counts(dropna=False))
    print(nt_client["est_revenu_6m"].value_counts(dropna=False))

