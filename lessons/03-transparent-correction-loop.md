# La boucle de correction transparente

Une passe de correction ne prouve pas qu'elle a appliqué la correction. Voici le
contrôle qui l'oblige à le prouver, et à le dire.

## Le défaut, mesuré en conditions réelles

Un client répond dans le fil : « commence la synthèse par la fréquentation plutôt
que par le chiffre d'affaires. » La boucle détecte la réponse, accuse réception,
régénère, franchit sa barrière de sortie, livre une version 2 en annonçant « voilà
la version corrigée ».

La comparaison bloc par bloc des deux fichiers donne le vrai résultat :

- la slide de synthèse de la V2 est **identique** à celle de la V1 ;
- les deux seules différences entre les deux versions portent sur **d'autres**
  slides, et ne correspondent à aucune demande du client.

Toute la mécanique fonctionnait. Le fond était en échec.

## Les deux causes, et elles sont distinctes

**Cause 1 : la demande était déjà satisfaite.** La slide commençait déjà par la
fréquentation : le titre, le premier indicateur et la première puce portaient tous
sur la fréquentation, le chiffre d'affaires venait en troisième position. La demande
du client était satisfaite avant qu'il la formule. La boucle ne pouvait rien
changer, et c'est une situation normale et fréquente.

**Cause 2 : la boucle ne l'a pas dit.** Elle a livré en annonçant une version
corrigée, sans dire que la demande était déjà satisfaite et sans dire ce qu'elle
avait effectivement modifié. Un client qui reçoit « voilà la version corrigée » et
retrouve la même page conclut que le système ne l'écoute pas. Le défaut de
communication est plus grave que le défaut de production.

Et par-dessus : les deux modifications non demandées **réparaient en silence** un
défaut de la version précédente (voir [la barrière d'ancrage des
sources](02-source-anchoring.md)). Une passe de correction qui modifie ce qu'on ne
lui a pas demandé, sans le déclarer, efface la trace de ses propres bugs.

## Les trois mécanismes à ajouter

### 1. Le diff de blocs entre la passe N et la passe N-1

Ouvrir réellement les deux documents, en extraire les blocs de texte dans l'ordre de
lecture (formes et cellules de tableau comprises), normaliser (accents, casse,
espaces) et comparer par appariement de séquences.

La sortie donne trois listes : blocs modifiés, ajoutés, retirés, chacun localisé par
sa page. Implémentation : [`code/block_diff.py`](../code/block_diff.py).

Ce contrôle est la seule chose qui a permis de détecter le défaut, et il tient en
une centaine de lignes. Il aurait dû exister avant la mise en service, pas après.

### 2. Le refus de livrer si la zone visée n'a pas bougé

La demande du client désigne une zone (une page, une section, un indicateur). Si
aucune différence n'apparaît dans cette zone, la livraison ne part pas telle quelle.
Deux issues acceptables, jamais une V2 muette :

- soit la production a échoué à appliquer la correction → c'est un échec de barrière,
  traité comme tel ;
- soit la demande était déjà satisfaite → cas 3.

### 3. La détection du « déjà satisfait », et sa réponse honnête

Quand le diff est vide sur la zone visée et que l'état du document satisfait déjà la
demande, la réponse au client est explicite :

> La synthèse commence déjà par la fréquentation : le titre, le premier indicateur
> et la première puce portent sur la fréquentation, le chiffre d'affaires vient
> ensuite. Dis-moi si tu voulais autre chose.

C'est une réponse qui **ne consomme pas une passe de correction** et qui rend la main
au client au lieu de simuler un travail.

## Et dans le mail de livraison : la liste de ce qui a changé

Le rendu humain du diff se met directement dans le corps du mail :

```
page 4 : « le chiffre d'affaires progresse de… » devient « la fréquentation
          progresse de… »
page 13, retrait : « Sources : … »
```

Cette liste a trois effets. Le client vérifie en dix secondes au lieu de relire tout
le document. Toute modification non demandée devient visible, donc discutable. Et le
système perd la possibilité de se corriger en silence.

## La règle générale

**Annoncer une correction n'est pas la prouver.** Toute boucle de correction
automatisée a besoin de trois choses avant sa mise en service : un diff mécanique
entre passes, un refus de livrer quand la zone visée n'a pas bougé, et une réponse
honnête au cas « déjà satisfait ».

Le diff n'est pas seulement un contrôle qualité interne : c'est le contenu du message
de livraison. La transparence sur ce qui a changé est moins coûteuse à produire
qu'une confiance perdue à réparer.
