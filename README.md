# Atelier Saint-Honoré — Projet Datamining (Sujet 7)

Projet de fin de module : analyse des clients d'une marque de maroquinerie de luxe
(770 lignes dans le fichier clients, 24 boutiques).

## Comment lancer le code

1. Installer pandas : `pip install pandas`
2. Se placer dans le dossier du projet.
3. Lancer `python preparation.py` : le message « Toutes les vérifications passent »
   doit s'afficher.

Les autres fichiers de code seront ajoutés par les branches suivantes.

## Étape 0 — Préparation des données
Voir les commentaires de `preparation.py` : une phrase par décision de nettoyage.

**H1 – Les directeurs de boutique pensent que la baisse est liée aux touristes.**
Selon les directeurs de boutique, la baisse du panier vient principalement des touristes, c'est-à-dire des clients qui habitent dans un autre pays que celui où se trouve la boutique.
Leur explication est assez simple : les touristes viennent souvent faire des achats ponctuels, par exemple pour acheter des cadeaux, et ne reviennent pas forcément pour effectuer d'autres achats.
Pour vérifier cette idée, je vais comparer le rapport_prochain des touristes avec celui des clients locaux. Je regarderai ensuite si les résultats changent selon le canal d'achat.

**H2 – L'équipe digitale pense que la baisse vient des achats en ligne.**
Pour l'équipe digitale, ce sont surtout les achats sur Internet qui expliquent la baisse du panier.
L'idée est que les clients qui achètent en ligne ont tendance à faire des achats plus rapides et parfois moins importants que ceux qui se rendent directement en boutique, où ils peuvent bénéficier des conseils des vendeurs.
Pour vérifier cette hypothèse, je vais comparer le rapport_prochain des clients qui achètent en boutique, en ligne ou sur les deux canaux. Je regarderai également si le fait d'être touriste ou local peut avoir une influence sur les résultats.

## Q2 — Le montant cumulé est-il un bon indicateur ?

## Q3 — Montant du prochain achat

## Q4 — Sur quels profils l'estimation est-elle fiable ?

## Q5 — Repérer les départs

## Q6 — 40 appels par boutique et par mois

## Q7 — Combien de types de clients ?

## Q8 — Quel traitement pour chaque groupe ?

## Q9 — Achats atypiques

## Synthèse
