import pandas as pd
from sympy import Si

ville_pays = {
    "Paris": "France", "Cannes": "France", "Bordeaux": "France",
    "Genève": "Suisse", "Londres": "Royaume-Uni", "Dubaï": "EAU",
    "Shanghai": "Chine", "Séoul": "Corée", "New York": "USA",
}

def initialisation ():
    """Cette fonction lit les deux fichiers CSV et renvoie le tableau des clients nettoyé.
    Elle ne prend rien en entrée (les fichiers doivent être dans le même dossier).
    Elle renvoie un tableau de 700 lignes et 23 colonnes, sans case vide.
    Règle du groupe : svp ne mettez pas une cible dans les colonnes qui servent à prédire,
    ni une colonne calculée à partir de la cible. Sinon le modèle triche, car la réponse
    est déjà dans les données.
      - Q3 et Q4 (on prédit montant_prochain_achat_eur) : ne pas utiliser rapport_prochain ni recule
      - Q5 et Q6 (on prédit depart) : ne pas utiliser est_revenu_6m ni depart
    """
    df = pd.read_csv("SaintHonore_clients.csv")
 # 70 lignes sont des copies exactes d'une autre ligne. Je les supprime pour qu'un client ne soit compté qu'une seule fois.
    df = df.drop_duplicates()
#harmonisation des colones montant
 # Le montant est en centimes (la médiane vaut 532 500, trop grand pour des euros),je divise par 100 pour avoir des euros, puis je supprime l'ancienne colonne parce qu'elle disait la même chose. 
    df["montant_euro"] = df["montant_total_centimes"] / 100
    df = df.drop(columns=["montant_total_centimes"])
 
#verification des incohérences sur la colonne panier_moyen_eur . Un panier vide ou négatif, ça n'existe pas.
# Je  recalcule avec la règle montant = achats x panier,qui est vraie pour tous les clients sans erreur.
    panier_impossible = df["panier_moyen_eur"].isna() | (df["panier_moyen_eur"] <= 0 ) 
    df.loc[panier_impossible , "panier_moyen_eur"] = df["montant_euro"] / df["nb_achats_12m"]

#verification des incohérences sur la colonne nb_achats_12m
    nb_achats_impossible = df["nb_achats_12m"].isna() | (df["nb_achats_12m"] <= 0) 
    df.loc[nb_achats_impossible , "nb_achats_12m"] = df["montant_euro"] / df["panier_moyen_eur"]

# remplacement des valeurs manquantes
# Pour les cartes vides, je ne sais pas si le client a une carte ou non je mets "Inconnue" et pas "aucune", sinon j'inventerais une information.
    df["carte_fidelite"] = df["carte_fidelite"].fillna("Inconnue")
    df["canal_prefere"] = df["canal_prefere"].fillna("Inconnu")
    df["pays_residence"] = df["pays_residence"].fillna("Inconnu")
    df["est_revenu_6m"] = df["est_revenu_6m"].fillna("Inconnu")

#"je lis le fichier des boutiques et j'ajoute le pays de chaque boutique. Ensuite je colle ces informations à chaque client avec merge.
    # how="left" : je garde tous les clients.
    # validate="many_to_one" : le programme s'arrête si une boutique apparaît deux fois,
    # car des clients seraient copiés en double sans que je le voie.""
    boutique = pd.read_csv("SaintHonore_boutiques.csv")
    boutique["pays_boutique"] = boutique["ville"].map(ville_pays)
    df = df.merge(boutique, left_on="boutique_principale", right_on="boutique_id", how="left" , validate="many_to_one")

# boutique_id donne la même information que boutique_principale, je la supprime.
    df= df.drop(columns = ["boutique_id"])

# ajout de la colonne touriste
# Un client est considéré comme touriste lorsqu’il habite dans un pays différent de celui où se trouve sa boutique. C’est notamment le cas des clients de Londres et de ceux qui habitent en Italie.
    df["touriste"] = (df["pays_residence"] != df["pays_boutique"]).astype(int)

# ajout de la colonne rapport_achats
    df["rapport_achats_pro"] = df["montant_prochain_achat_eur"] / df["panier_moyen_eur"]
# ajout de la colonne reculement
# Si c'est plus petit que 1, le client dépense moins que d'habitude : je dis qu'il "recule".
    df["recule"] = (df["rapport_achats_pro"] < 1).astype(int)
# ajout de la colonne la part des achats qui aboutissent a un retour
#La part de retours correspond au nombre de retours par rapport aux achats. Certains clients retournent plus de produits qu’ils n’en achètent, mais je les conserve pour pouvoir les utiliser dans la question 9.
    df["part_retours"] = df["retours"] / df["nb_achats_12m"]
# ajout de la colonne des clients qui ne sont pas revenus depuis 6 mois
    df["depart"] = (df["est_revenu_6m"] == "non").astype(int)

    return df

if __name__ == "__main__":
    nt_client = initialisation()
    pd.set_option("display.float_format", "{:.2f}".format)

    assert nt_client.shape == (700, 23), nt_client.shape
    assert nt_client.isna().sum().sum() == 0, "cases vides restantes"
    assert nt_client.duplicated().sum() == 0, "doublons restants"
    assert nt_client["client_id"].is_unique, "client_id en double"
    assert (nt_client["nb_achats_12m"] >= 1).all(), "achats < 1"
    assert (nt_client["panier_moyen_eur"] > 0).all(), "panier <= 0"
    assert ((nt_client["nb_achats_12m"] * nt_client["panier_moyen_eur"] - nt_client["montant_euro"]).abs() < 1).all(), "règle montant cassée"
    for col in ["touriste", "recule", "depart"]:
        assert nt_client[col].isin([0, 1]).all(), col
    assert nt_client["depart"].sum() == 412, nt_client["depart"].sum()
   
    print(nt_client.shape)
    print(nt_client.head(5))
    print(nt_client.describe().T)

