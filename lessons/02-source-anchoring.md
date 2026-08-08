# La barrière d'ancrage des sources

Un contrôle qui refuse de livrer un document citant une source qui n'a jamais été
déposée.

## Le défaut, tel qu'il s'est produit

Un rapport mensuel livré à un client portait en pied de slide une ligne du type :

```
Sources : direction du centre (trois enseignes nommées)
```

La direction n'avait rien déposé de tel. Le dépôt contenait trois pièces, toutes
identifiées, et aucune ne portait cette information. **L'attribution était
inventée.**

Deux choses aggravent le cas, et ce sont elles qui portent la leçon.

**La barrière de sortie existante ne l'a pas vue.** Elle contrôlait l'existence du
fichier, sa taille, son ouverture réelle, le nombre de pages, l'absence de traces de
fabrication et les règles de mise en page. Six contrôles sérieux, et aucun ne porte
sur la véracité d'une attribution de source. Une barrière de sortie mesure la forme ;
la forme était parfaite.

**La version suivante a réparé le défaut en silence.** Lors d'une passe de
correction demandée pour une autre raison, la ligne de sources a été retirée. Rien,
dans le mail de livraison, ne le mentionnait. Le défaut ne s'est donc découvert
qu'en comparant les deux versions bloc par bloc, plusieurs jours plus tard. Un
système qui se corrige sans le dire supprime la trace de son propre défaut.

## Le contrôle qui ferme la porte

Le principe est volontairement sévère : **une étiquette de source n'existe que si
elle est déclarée dans la configuration, et une étiquette adossée à une pièce n'est
autorisée que si la pièce qui la porte est réellement au dépôt.**

Deux catégories déclarées, et rien d'autre :

- **adossées** : l'étiquette n'est valide que si un fichier du dépôt correspond à un
  motif de nom déclaré pour elle ;
- **libres** : étiquettes autorisées sans pièce (emplacements réservés, sources
  publiques vérifiées une par une par l'exploitant).

Tout segment de ligne de sources qui ne contient aucune étiquette déclarée est un
échec de barrière, avec le libellé fautif cité tel quel dans le verdict.

Deux refus supplémentaires, qui comptent autant :

- **aucune liste déclarée en configuration** → échec, et non pas passage silencieux.
  Un contrôle qui se désactive quand sa configuration manque ne contrôle rien.
- **aucune mention de source dans le document** → échec. Un rapport sans source
  citée n'est pas livrable.

Implémentation : [`code/source_anchoring.py`](../code/source_anchoring.py).

## Pourquoi une liste fermée, et pas une vérification sémantique

La tentation est de demander à un modèle si l'attribution est plausible. C'est
exactement le mécanisme qui a produit le défaut. Une liste fermée déclarée en
configuration a trois propriétés qu'aucune vérification par modèle n'a :

1. elle est **déterministe** : même document, même verdict, toujours ;
2. elle ne dépend pas du vocabulaire du rédacteur, seulement de la présence d'une
   étiquette connue ;
3. elle est **auditable par le client**, qui peut lire la liste des sources que le
   système s'autorise à citer et la valider une fois pour toutes.

Le contrôle ne juge pas la vérité du contenu. Il vérifie que le document ne cite
comme source que ce qui a été déposé ou déclaré. C'est un périmètre étroit, et c'est
ce qui le rend tenable.

## La règle générale à retenir

**Une barrière de sortie doit contrôler l'ancrage, pas seulement la forme.** Pour
chaque affirmation d'origine que le document porte (source, auteur, date d'un
chiffre, pièce de référence), il faut un contrôle mécanique qui la confronte à la
liste fermée des entrées réellement reçues.

Le corollaire vaut au-delà des rapports : dès qu'un système génère du texte qui
attribue une information à quelqu'un, l'attribution est le premier endroit où il
hallucine, et le dernier où on regarde.
