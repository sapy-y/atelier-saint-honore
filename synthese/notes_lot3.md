# Lot 3 : Q5 (risque de départ) et Q6 (ciblage des appels)

- Sur 700 clients uniques (après suppression de 70 doublons), 59 % ne sont pas revenus dans les six mois.
- Nous avons comparé trois modèles (régression logistique, arbre, forêt aléatoire) et retenu la forêt aléatoire, mais le départ reste difficile à prévoir : ROC-AUC de 0,59 sur le test, un peu mieux que le hasard.
- Les signaux qui annoncent un départ sont surtout le montant cumulé, le nombre d'achats sur 12 mois et l'ancienneté : les clients partis ont moins dépensé, moins acheté et sont plus récents.
- Nous proposons d'appeler les clients au-dessus de 0,80 de probabilité de départ, 40 par boutique au maximum : cela fait 29 appels, dont 83 % concernent des clients réellement partis (contre 59 % au hasard).
- Le prix de cette prudence : nous n'atteignons que 6 % des partants ; à 0,70 on appelle 143 clients avec 70 % de précision, un compromis à discuter avec la direction.
