import pandas as pd
from preparation import initialisation


def bornes_iqr(serie):
    """Calcule les bornes basse et haute d'une colonne avec la méthode IQR.
    Entrée : une colonne pandas (Series).
    Sortie : un tuple (borne_inf, borne_sup).
    """
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    borne_inf = q1 - 1.5 * iqr
    borne_sup = q3 + 1.5 * iqr
    return (borne_inf, borne_sup)


def atypiques(df):
    """
Repère les clients qui ont un comportement inhabituel par rapport aux autres.
Par exemple, ceux qui dépensent beaucoup plus, effectuent beaucoup plus d'achats 
ou font beaucoup plus de retours que la moyenne du groupe.

Entrée : le tableau des clients après nettoyage.
Sortie : un tableau qui contient uniquement les clients ayant un comportement inhabituel.

"""
# On regarde uniquement les valeurs les plus élevées, car les valeurs les plus faibles ne permettent pas de repérer de clients particuliers.
    _, haut_panier = bornes_iqr(df["panier_moyen_eur"])
    _, haut_achat = bornes_iqr(df["nb_achats_12m"])
    _, haut_retour = bornes_iqr(df["retours"])
    _, haut_part = bornes_iqr(df["part_retours"])

    #  un client est atypique s'il dépasse au moins un seuil
    est_atypique = (
        (df["panier_moyen_eur"] > haut_panier)
        | (df["nb_achats_12m"] > haut_achat)
        | (df["retours"] > haut_retour)
        | (df["part_retours"] > haut_part)
    )
    return df[est_atypique]


if __name__ == "__main__":
    df = initialisation()

    colonnes = ["panier_moyen_eur", "nb_achats_12m", "retours", "part_retours"]

    for colonne in colonnes:
        _, haut = bornes_iqr(df[colonne])
        extremes = df[df[colonne] > haut]
        print("Colonne :", colonne)
        print("Borne haute :", haut)
        print("Clients extrêmes :", len(extremes))
        print(extremes[colonne].describe())
        print()

    liste_atypiques = atypiques(df)
    print("Clients atypiques (au moins une colonne) :", len(liste_atypiques))
