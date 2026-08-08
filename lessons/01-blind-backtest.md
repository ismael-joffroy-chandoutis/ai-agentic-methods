# Backtest à l'aveugle d'un contrôle documentaire

Comment savoir si un contrôle automatisé de dossiers vaut quelque chose, avant de le
vendre ou de le mettre en service.

## Le problème

Un système qui relit des dossiers réglementaires produit une liste de constats.
Rien, dans cette liste, ne dit si elle est bonne. On peut la trouver impressionnante
et se tromper complètement : un contrôle bavard qui rate le point critique est pire
qu'un contrôle silencieux, parce qu'il inspire confiance.

Le seul étalon disponible est le travail humain déjà fait sur le même dossier.

## Le protocole

1. **Trouver un dossier réel déjà instruit par un humain**, avec ses passes de
   correction successives. Un dossier instruit en trois passes sur onze jours donne
   trois listes de remarques datées : c'est l'étalon.
2. **Faire tourner le contrôle à l'aveugle.** Il ne voit jamais les remarques
   humaines. Il reçoit les états du dossier et le référentiel réglementaire, rien
   d'autre. C'est la condition sans laquelle la mesure ne veut rien dire.
3. **Découper le contrôle en thèmes** et faire tourner un contrôle par thème sur
   chaque état du dossier. Chaque constat cite obligatoirement la pièce, l'article
   et une sévérité.
4. **Comparer ensuite**, constat par constat, contre les remarques humaines.
   Barème : trouvé = 1, partiellement = 0,5, raté = 0. Cela donne un rappel strict
   et un rappel pondéré.
5. **Mesurer aussi la précision**, c'est-à-dire la part des constats du système qui
   sont fondés. Un rappel élevé avec une précision faible est un système qui noie
   l'instructeur.

## Ce que la mesure a donné

Sur un dossier d'autorisation de travaux réel, 45 remarques humaines réparties sur
trois passes, 118 constats produits par le contrôle :

| Mesure | Valeur |
|---|---|
| Rappel strict | 71,1 % |
| Rappel pondéré | 80,0 % |
| Précision | 99,2 % (1 constat douteux sur 118) |
| Constats fondés sans équivalent humain | 31 |
| Volume relatif | environ 2,6 fois plus de constats que l'humain |

## Les trois enseignements qui se généralisent

**Les ratés ne sont jamais réglementaires, ils sont « de guichet ».** Les cinq
remarques humaines manquées portaient toutes sur des pièces de pratique locale
(formulaires internes du bailleur, attendus non écrits de la commission) absentes
du référentiel. Le système ne peut pas inventer une exigence qui n'est écrite
nulle part. Corollaire opérationnel : la façon la moins chère d'augmenter le rappel
n'est pas de retoucher le contrôle, c'est de demander au client sa check-list de
pièces type.

**La précision compte plus que le rappel, et elle s'obtient par le format.**
Imposer à chaque constat de citer une pièce et un article rend l'erreur non
seulement rare mais détectable en relecture. Un constat sans référence n'est pas
vérifiable, donc pas utilisable, donc à refuser à la source.

**Un étalon humain n'est pas une vérité.** Une remarque humaine a été levée pièce
en main par le contrôle : l'élément réputé absent figurait bien au dossier. Le
rappel mesure donc la couverture des remarques humaines, pas leur justesse. C'est
précisément l'intérêt d'une seconde lecture systématique, et il faut le dire dans
le rapport plutôt que de présenter l'humain comme l'oracle.

## La passe de fusion, sans laquelle le résultat est inutilisable

118 constats bruts ne se lisent pas. Une passe de consolidation les regroupe par
classe de défaut, unifie la hiérarchie, les range par pièce du dossier et écrit une
synthèse d'avis en tête. Sur le corpus mesuré : 118 constats bruts donnent 84
constats consolidés, et 69 en donnent 46 sur le dossier complet.

C'est l'équivalent machine du « je vous ai mis en gras les points les plus
critiques » d'un instructeur. Sans elle, le livrable est une décharge de constats
que personne ne lit. Implémentation distillée : [`code/merge_findings.py`](../code/merge_findings.py).

Point de conception important : la fusion est **déterministe par défaut**. Le
rapprochement de libellés proches par un modèle est une option désactivée, pour que
la même entrée donne toujours la même sortie et que le résultat soit rejouable
gratuitement.

## Le piège du corpus, à traiter avant de lancer le backtest

**C'est l'erreur qui a le plus coûté, et elle est structurelle.** Le corpus de test
ne correspondait exactement à aucune passe humaine : l'état initial archivé ne
contenait pas le formulaire que l'instructeur avait sous les yeux, et l'état
« complet » intégrait déjà six demandes de la deuxième passe. Rappel et divergences
se mesurent donc partiellement contre le mauvais objet.

Conséquence pour tout backtest futur : **figer une archive datée du dossier
exactement tel qu'il était à chaque passe humaine**, avant de commencer. Sans cela,
un écart de mesure ne se distingue pas d'un écart de corpus, et aucun chiffre n'est
défendable.

Autres limites à déclarer explicitement dans le rapport :

- une passe comparée « par anticipation » (aucun contrôle n'a tourné sur la version
  définitive) n'est pas une mesure de rappel, c'est une observation ;
- un état qui ne contient que des plans mesure surtout la capacité à constater des
  absences, pas à analyser des pièces écrites ;
- les zones illisibles à l'échelle disponible ne se tranchent pas et doivent être
  signalées comme telles.

## Ce que le backtest sert vraiment à dire

Pas « le système remplace l'humain ». La conclusion défendable est plus précise et
se vend mieux : le contrôle produit en une passe, avant la première relecture
humaine, l'équivalent de la couverture de trois passes d'instruction, et il ajoute
des constats que trois passes n'avaient pas vus. L'humain garde la décision et la
pratique non écrite. C'est un déplacement du travail, pas une substitution.
