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


# Portrait des 5 groupes (étapes 5 et 6, chiffres de la sortie du script) :
# 0 "Gros clients fidèles"  : 57 clients, panier ~6 700 €, ~10 achats par an, peu de retours.
#                             Le moins de départs (35 %) et le plus gros prochain achat (~4 300 €).
# 1 "Récents occasionnels"  : 251 clients, panier ~2 200 €, 2 achats, 1 an et demi d'ancienneté,
#                             aucune demande SAV. 66 % ne reviennent pas.
# 2 "Récents avec SAV"      : 173 clients, comme le groupe 1 mais avec en moyenne 1,3 demande SAV.
#                             66 % ne reviennent pas.
# 3 "Anciens réguliers"     : 179 clients, ~5 ans d'ancienneté, panier plus petit (~1 700 €),
#                             3 à 4 achats par an. 52 % de départs.
# 4 "Gros acheteurs à retours" : 40 clients, panier ~5 900 €, ~9 achats, 2,6 retours en moyenne.
#                             Retours en série : à croiser avec Q9 (revente parallèle ?).
NOMS_GROUPES = {
    0: "Gros clients fidèles",
    1: "Récents occasionnels",
    2: "Récents avec SAV",
    3: "Anciens réguliers",
    4: "Gros acheteurs à retours",
}

# Conclusion sur les 3 cartes de 2015 :
# chaque groupe contient à peu près la même part de cartes que le fichier entier
# (environ 48 % sans carte, 35 % argent, 14 % or). Les gros clients fidèles n'ont pas plus
# souvent la carte or que les récents occasionnels. La carte ne suit donc pas la valeur
# réelle des clients : les niveaux de 2015 sont à refaire à partir de ces groupes.


def decrire_groupes(df):
    """Étape 5 : portrait de chaque groupe sur les colonnes qui ont servi à le former.
    Entrée : le tableau des clients avec la colonne "groupe".
    Sortie : effectif, moyenne et médiane de chaque colonne, par groupe.
    On donne la médiane en plus de la moyenne car quelques très gros paniers
    tirent la moyenne vers le haut.
    """
    effectif = df.groupby("groupe").size().rename("effectif")
    moyennes = df.groupby("groupe")[COLONNES].mean().add_prefix("moy_")
    medianes = df.groupby("groupe")[COLONNES].median().add_prefix("med_")
    return pd.concat([effectif, moyennes, medianes], axis=1)


def regarder_hors_modele(df):
    """Étape 6 : on regarde les colonnes qui n'ont PAS servi à former les groupes.
    Elles disent si les groupes sont utiles : s'ils se distinguent aussi sur le retour
    à 6 mois ou le prochain achat, ce ne sont pas des groupes au hasard.
    Sortie : deux tableaux, les indicateurs par groupe et la répartition des cartes.
    """
    indicateurs = df.groupby("groupe").agg(
        taux_depart=("depart", "mean"),
        prochain_achat_moyen=("montant_prochain_achat_eur", "mean"),
        part_touristes=("touriste", "mean"),
        part_en_ligne=("canal_prefere", lambda c: (c == "en ligne").mean()),
        part_mixte=("canal_prefere", lambda c: (c == "mixte").mean()),
    )
    # normalize="index" : chaque ligne fait 100 %, on lit la part de chaque carte dans le groupe.
    cartes = pd.crosstab(df["groupe"], df["carte_fidelite"], normalize="index")
    return indicateurs, cartes


# Q8 : quel traitement pour chaque groupe, et lequel pèse le plus dans le chiffre d'affaires ?

# Nombre de clients encartés dans toute l'entreprise (donné par le sujet).
NB_CLIENTS_TOTAL = 6400


def chiffre_affaires_groupes(df):
    """Étape 1 et 2 de Q8 : poids de chaque groupe.
    Entrée : le tableau des clients avec la colonne "groupe".
    Sortie : un tableau avec, par groupe, l'effectif, le chiffre d'affaires sur 12 mois,
    sa part du total, le CA médian par client, le taux de départ, le prochain achat moyen
    et le CA extrapolé à toute la clientèle.
    """
    # montant_euro = achats sur 12 mois x panier moyen (vérifié à l'étape 0) :
    # c'est donc bien le chiffre d'affaires des 12 derniers mois de chaque client.
    t = df.groupby("groupe").agg(
        effectif=("client_id", "size"),
        ca_12m=("montant_euro", "sum"),
        ca_median_client=("montant_euro", "median"),
        taux_depart=("depart", "mean"),
        prochain_achat_moyen=("montant_prochain_achat_eur", "mean"),
    )
    t["part_ca"] = t["ca_12m"] / t["ca_12m"].sum()
    # Extrapolation : le fichier est un extrait de 700 clients sur 6 400. On multiplie par
    # 6 400 / 700. Cela suppose que l'extrait est représentatif de toute la clientèle,
    # ce que personne ne nous garantit : c'est un ordre de grandeur, pas un chiffre exact.
    t["ca_extrapole"] = t["ca_12m"] * NB_CLIENTS_TOTAL / len(df)
    return t


# Ce qu'on appelle "forte valeur" : on juge un client sur son CA des 12 derniers mois,
# mais par la médiane du groupe, pas par le montant cumulé seul (Q2 montre qu'il classe mal
# les clients pris un par un). Seuils pris sur tout le fichier, pour ne rien inventer :
# - forte valeur  : CA médian du groupe au-dessus du quart supérieur du fichier (9 277 €) ;
# - valeur moyenne : au-dessus de la médiane du fichier (5 309 €) ;
# - faible valeur : en dessous.
# "Départs fréquents" : plus de 40 % du groupe ne revient pas sous 6 mois. Le fichier entier
# est à 59 %, mais chez des clients qui rapportent 50 000 € par an, perdre presque un sur
# deux coûte trop cher pour ne rien faire.
SEUIL_DEPART = 0.40


def choisir_traitement(ligne, seuil_fort, seuil_moyen):
    """Étape 3 de Q8 : un traitement par groupe, selon la règle de la direction.
    - forte valeur et départs fréquents : relance (un vendeur rappelle le client) ;
    - forte valeur et fidèle : avant-première de la collection ;
    - valeur moyenne : invitation à la collection ;
    - faible valeur : rien (on ne dépense pas d'attention là où elle ne rapporte pas).
    """
    if ligne["ca_median_client"] >= seuil_fort:
        if ligne["taux_depart"] > SEUIL_DEPART:
            return "relance"
        return "avant-première"
    if ligne["ca_median_client"] >= seuil_moyen:
        return "invitation"
    return "rien"


def tableau_q8(df):
    """Réunit le poids de chaque groupe et son traitement, du plus gros CA au plus petit."""
    t = chiffre_affaires_groupes(df)
    seuil_fort = df["montant_euro"].quantile(0.75)
    seuil_moyen = df["montant_euro"].median()
    t["traitement"] = t.apply(choisir_traitement, axis=1, args=(seuil_fort, seuil_moyen))
    t.index = t.index.map(NOMS_GROUPES)
    return t.sort_values("ca_12m", ascending=False)


# Résultat (sortie du script) :
# - Gros clients fidèles : 57 clients (8 %) mais 41 % du CA, environ 33 M€ extrapolés.
#   C'est le groupe qui pèse le plus. Traitement : avant-première.
# - Gros acheteurs à retours : 40 clients, 22 % du CA (~18 M€ extrapolés), 47,5 % de départs.
#   Traitement : relance, MAIS après la vérification de Q9 : leurs retours en série peuvent
#   cacher de la revente parallèle, et on ne relance pas un revendeur.
# - Anciens réguliers : valeur moyenne, 12 % du CA. Traitement : invitation.
# - Récents occasionnels et récents avec SAV : faible valeur, 25 % du CA à eux deux.
#   Traitement : rien, même s'ils partent souvent (66 %).


if __name__ == "__main__":
    pd.set_option("display.float_format", "{:.2f}".format)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)

    clients = initialisation()
    X = standardiser(clients)

    print("=== Q7 : choix du nombre de groupes ===")
    print(choisir_k(X))
    print("Graphique enregistré : q7_choix_k.png")

    modele = faire_groupes(X, K_CHOISI)
    clients["groupe"] = modele.labels_
    print("\nEffectif de chaque groupe (k =", K_CHOISI, ") :")
    print(clients["groupe"].map(NOMS_GROUPES).value_counts())

    print("\n=== Q7 : portrait des groupes ===")
    print(decrire_groupes(clients).T)

    indicateurs, cartes = regarder_hors_modele(clients)
    print("\n=== Q7 : colonnes non utilisées pour former les groupes ===")
    print(indicateurs)
    print("\nRépartition des cartes dans chaque groupe :")
    print(cartes)
    print("\nRépartition des cartes dans tout le fichier :")
    print(clients["carte_fidelite"].value_counts(normalize=True))

    print("\n=== Q8 : poids et traitement de chaque groupe ===")
    q8 = tableau_q8(clients)
    print(q8)
    print("\nCA total du fichier sur 12 mois :", round(q8["ca_12m"].sum()), "€")
    print("CA total extrapolé à", NB_CLIENTS_TOTAL, "clients :", round(q8["ca_extrapole"].sum()), "€")
