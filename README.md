# Projet Datamining : Atelier Saint-Honoré

Projet de fin de module : analyse des clients d'une marque de maroquinerie de luxe

## Comment lancer le code

1. Installer pandas : `pip install pandas`
2. Se placer dans le dossier du projet.
3. Lancer `python preparation.py` : le message « Toutes les vérifications passent »
   doit s'afficher.

Les autres fichiers de code seront ajoutés par les branches suivantes.

## Q1 : D'où vient la baisse du panier moyen ?

Voir les commentaires de `preparation.py` : une phrase par décision de nettoyage.

**H1 – Les directeurs de boutique pensent que la baisse est liée aux touristes.**
Selon les directeurs de boutique, la baisse du panier vient principalement des touristes, c'est-à-dire des clients qui habitent dans un autre pays que celui où se trouve la boutique.
Leur explication est assez simple : les touristes viennent souvent faire des achats ponctuels, par exemple pour acheter des cadeaux, et ne reviennent pas forcément pour effectuer d'autres achats.
Pour vérifier cette idée, je vais comparer le rapport_prochain des touristes avec celui des clients locaux. Je regarderai ensuite si les résultats changent selon le canal d'achat.

**H2 – L'équipe digitale pense que la baisse vient des achats en ligne.**
Pour l'équipe digitale, ce sont surtout les achats sur Internet qui expliquent la baisse du panier.
L'idée est que les clients qui achètent en ligne ont tendance à faire des achats plus rapides et parfois moins importants que ceux qui se rendent directement en boutique, où ils peuvent bénéficier des conseils des vendeurs.
Pour vérifier cette hypothèse, je vais comparer le rapport_prochain des clients qui achètent en boutique, en ligne ou sur les deux canaux. Je regarderai également si le fait d'être touriste ou local peut avoir une influence sur les résultats.

## Q2 : Le montant cumulé est-il un bon indicateur ?

## Q3 : Montant du prochain achat

## Q4 : Sur quels profils l'estimation est-elle fiable ?

## Q5 : Repérer les départs

## Q6 : 40 appels par boutique et par mois

## Q7 : Combien de types de clients ?

La question revient à se demander si les 3 niveaux de carte (aucune, argent, or) correspondent à de vrais types de clients. Il n'y a rien à prédire ici, donc j'ai utilisé le k-means pour regrouper les clients qui se ressemblent.

Pour former les groupes, j'ai pris le panier moyen, le nombre d'achats sur 12 mois, l'ancienneté, les retours et les demandes SAV. J'ai laissé de côté la carte, puisque c'est elle qu'on veut juger, le montant cumulé, qui répète achats × panier (voir Q2), et les deux cibles, qui servent seulement à décrire les groupes après coup. Les colonnes sont standardisées avant le k-means, sinon le panier, qui se compte en milliers d'euros, aurait pesé beaucoup plus que les retours.

Pour choisir le nombre de groupes, j'ai regardé la méthode du coude (k de 1 à 7) et la silhouette (k de 2 à 6) : voir `q7_choix_k.png`. La silhouette est la meilleure pour k = 2 (0,46), mais ces deux groupes séparent seulement 99 gros clients du reste, ce qui ne suffit pas pour décider de plusieurs traitements. De k = 3 à k = 6, la silhouette reste autour de 0,30 et le coude se plie vers 3-4, donc les deux méthodes ne tranchent pas. J'ai choisi k = 5 parce que c'est à partir de là que les gros clients se séparent en deux profils qui ne se traitent pas de la même façon. Je n'ai pas pris 3 juste parce qu'il y a 3 cartes.

J'ai aussi refait les groupes sans les 152 clients atypiques de Q9. Les deux groupes de gros clients disparaissent presque entièrement (91 de leurs 97 clients sont atypiques) et la silhouette baisse à 0,20. Je garde donc tous les clients : les enlever reviendrait à enlever ceux qui font plus de 60 % du chiffre d'affaires.

Les 5 groupes (sur 700 clients) :

| Groupe | Clients | Portrait | Ne reviennent pas |
|---|---|---|---|
| Gros clients fidèles | 57 | panier d'environ 6 700 €, une dizaine d'achats par an, peu de retours | 35 % |
| Gros acheteurs à retours | 40 | panier d'environ 5 900 €, 8 à 9 achats, mais 2,6 retours en moyenne | 47 % |
| Anciens réguliers | 179 | clients depuis 5 ans en moyenne, 3 à 4 achats par an, panier plus petit (1 700 €) | 52 % |
| Récents occasionnels | 251 | un an et demi d'ancienneté, 2 achats, panier d'environ 2 200 €, aucun SAV | 66 % |
| Récents avec SAV | 173 | même profil que les précédents, mais avec 1,3 demande SAV en moyenne | 66 % |

Conclusion : on a 5 types de clients, et les cartes n'y correspondent pas. Dans chaque groupe, on retrouve à peu près la même répartition que dans tout le fichier (environ 48 % sans carte, 35 % argent, 14 % or). Les gros clients fidèles n'ont pas plus souvent la carte or que les clients récents. C'est vrai aussi quand on enlève les atypiques.

Recommandation : refaire les niveaux du programme de fidélité à partir de ces groupes plutôt que de garder ceux de 2015. Aujourd'hui, la carte or ne permet pas de reconnaître les clients qui rapportent le plus.

## Q8 : Quel traitement pour chaque groupe ?

Pour chaque groupe, j'ai calculé le chiffre d'affaires des 12 derniers mois (somme du montant de chaque client), sa part du total et le taux de clients qui ne reviennent pas. J'ai ensuite extrapolé à toute la clientèle en multipliant par 6 400 / 700. Ça suppose que les 700 clients du fichier sont représentatifs des 6 400, ce qu'on ne peut pas vérifier : les montants extrapolés sont des ordres de grandeur.

J'ai jugé la valeur d'un groupe sur le chiffre d'affaires médian de ses clients, et pas sur le montant cumulé client par client, puisque Q2 montre qu'il classe mal les clients pris un par un. Un groupe est de forte valeur si sa médiane dépasse le quart supérieur du fichier (9 277 €), de valeur moyenne si elle dépasse la médiane du fichier (5 309 €), et de faible valeur sinon. Pour les départs, j'ai mis la limite à 40 % : chez des clients qui rapportent autour de 50 000 € par an, en perdre presque un sur deux coûte trop cher pour ne rien faire.

| Groupe | CA sur 12 mois | Part du CA | CA extrapolé (6 400 clients) | Traitement |
|---|---|---|---|---|
| Gros clients fidèles | 3,63 M€ | 41 % | environ 33 M€ | avant-première |
| Gros acheteurs à retours | 1,96 M€ | 22 % | environ 18 M€ | relance, après vérification |
| Récents occasionnels | 1,21 M€ | 14 % | environ 11 M€ | rien |
| Anciens réguliers | 1,10 M€ | 12 % | environ 10 M€ | invitation |
| Récents avec SAV | 0,96 M€ | 11 % | environ 9 M€ | rien |

Le groupe qui pèse le plus est celui des gros clients fidèles : 8 % des clients, mais 41 % du chiffre d'affaires, soit environ 33 M€ par an sur toute la clientèle si le fichier est représentatif. Ce sont eux qu'il faut soigner en priorité, avec l'avant-première de la collection.

Les gros acheteurs à retours rapportent beaucoup et presque la moitié ne revient pas, ce qui justifierait une relance. Mais leurs retours en série peuvent cacher de la revente parallèle : il faut d'abord vérifier leurs dossiers (Q9) et ne relancer que ceux qui sont de vrais clients.

Les anciens réguliers ont une valeur moyenne : une invitation à la collection suffit. Pour les deux groupes de clients récents, même s'ils partent souvent, leur valeur reste faible et on ne leur envoie rien de particulier. Au total, l'avant-première et la relance concernent moins de 100 clients sur 700, mais 63 % du chiffre d'affaires.

## Q9 : Achats atypiques

## Synthèse
