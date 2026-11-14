import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from preparation import initialisation

# Q7 : combien de types de clients a-t-on vraiment ?
# Il n'y a pas de cible (on ne cherche pas à prédire une colonne) : on regroupe les clients
# qui se ressemblent, avec le clustering k-means vu en cours.

# Étape 1 : les colonnes utilisées pour former les groupes.
# - panier, achats, ancienneté : ce qu'un client dépense, à quelle fréquence, depuis quand.
# - retours et demandes SAV : la façon dont il se comporte après l'achat.
# Colonnes écartées :
# - les cibles (montant_prochain_achat_eur, est_revenu_6m) et ce qui en est calculé
#   (rapport_achats_pro, recule, depart) : on s'en sert après, pour juger les groupes.
# - montant_euro : il vaut exactement achats x panier (vérifié à l'étape 0, et Q2 montre
#   qu'il répète ces deux colonnes). Le garder compterait deux fois la même information.
# - carte_fidelite : c'est justement elle qu'on veut juger. Si on la met dedans, on
#   retrouve forcément les cartes dans les groupes.
COLONNES = ["panier_moyen_eur", "nb_achats_12m", "anciennete_mois", "retours", "demandes_sav"]

# Nombre de groupes retenu à l'étape 3 (voir la justification plus bas).
K_CHOISI = 5


def standardiser(df):
    """Met les colonnes de COLONNES à la même échelle (moyenne 0, écart-type 1).
    Entrée : le tableau des clients.
    Sortie : un tableau de nombres prêt pour k-means.
    Sans ça, le panier (en milliers d'euros) écraserait les retours (0 à 5) :
    k-means calcule des distances, donc la colonne aux plus grands nombres déciderait seule.
    """
    return StandardScaler().fit_transform(df[COLONNES])


def faire_groupes(X, k):
    """Lance k-means avec k groupes et renvoie le modèle entraîné.
    n_init=10 : on essaie 10 points de départ et on garde le meilleur, car k-means
    peut tomber sur une mauvaise solution selon son départ.
    random_state=42 : tout le monde obtient les mêmes groupes en relançant le code.
    """
    return KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)


def choisir_k(X):
    """Calcule l'inertie (coude, k de 1 à 7) et la silhouette (k de 2 à 6).
    Entrée : les données standardisées.
    Sortie : un tableau avec une ligne par valeur de k, et un graphique enregistré.
    """
    lignes = []
    for k in range(1, 8):
        modele = faire_groupes(X, k)
        # La silhouette n'existe pas pour un seul groupe.
        if 2 <= k <= 6:
            silhouette = silhouette_score(X, modele.labels_)
        else:
            silhouette = None
        lignes.append({"k": k, "inertie": modele.inertia_, "silhouette": silhouette})
    resultats = pd.DataFrame(lignes)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(resultats["k"], resultats["inertie"], marker="o")
    ax1.set_title("Méthode du coude")
    ax1.set_xlabel("nombre de groupes k")
    ax1.set_ylabel("inertie")
    avec_silhouette = resultats.dropna(subset=["silhouette"])
    ax2.plot(avec_silhouette["k"], avec_silhouette["silhouette"], marker="o", color="darkorange")
    ax2.set_title("Score de silhouette")
    ax2.set_xlabel("nombre de groupes k")
    fig.tight_layout()
    fig.savefig("q7_choix_k.png", dpi=120)
    plt.close(fig)
    return resultats


# Étape 3 : choix de k.
# Résultats obtenus (700 clients) :
#   k   inertie   silhouette
#   2    2437       0,46
#   3    1919       0,30
#   4    1560       0,30
#   5    1377       0,30
#   6    1226       0,30
# - La silhouette est la plus haute pour k=2, mais ces 2 groupes séparent seulement
#   99 gros clients des 601 autres : trop grossier pour décider 4 traitements différents.
# - De k=3 à k=6, la silhouette est la même (0,30) : elle ne permet pas de choisir.
# - Le coude se plie vers k=3 ou 4, puis la baisse de l'inertie ralentit.
# Les deux méthodes hésitent, donc on tranche avec le métier : avec k=5, les gros clients
# se coupent en deux groupes qui ne demandent pas le même traitement :
# des gros clients fidèles avec peu de retours, et des gros acheteurs avec des retours
# en série (à rapprocher de Q9). Avec k=4, ces deux profils restent mélangés.
# On ne prend pas k=3 juste parce qu'il y a 3 cartes : c'est la carte qu'on veut juger.


if __name__ == "__main__":
    pd.set_option("display.float_format", "{:.2f}".format)
    pd.set_option("display.width", 200)

    clients = initialisation()
    X = standardiser(clients)

    print("=== Q7 : choix du nombre de groupes ===")
    print(choisir_k(X))
    print("Graphique enregistré : q7_choix_k.png")

    modele = faire_groupes(X, K_CHOISI)
    clients["groupe"] = modele.labels_
    print("\nEffectif de chaque groupe (k =", K_CHOISI, ") :")
    print(clients["groupe"].value_counts().sort_index())
