# Un référentiel incomplet, et le comportement qui sauve la mise

Le cas d'école : le référentiel manquait la moitié de la règle la plus courante du
domaine, et c'est le contrôle qui a rendu la lacune visible — parce qu'il a dit qu'il
ne savait pas.

## Le cas

Un contrôle automatisé relit un dossier technique. Les plans du bureau d'études
calculent une distance réglementaire par une formule (une distance maximale égale à
quatre fois une hauteur de référence) sans citer le paragraphe qui la fonde.

Le référentiel constitué pour le contrôle ne portait, sur ce point, qu'une **borne
absolue** : 30 mètres. Rien sur la formule proportionnelle.

Trois comportements étaient possibles :

1. **affirmer que la formule n'existe pas** et opposer au preneur une demande de
   correction fausse ;
2. **valider en silence**, faute de règle contraire ;
3. **signaler l'incertitude** : relever la formule, dire qu'elle n'est pas recoupable
   dans le référentiel, et écrire ne pouvoir « ni la valider ni l'infirmer sur
   pièces ».

Le contrôle a choisi le troisième. Vérification menée le lendemain sur le texte
réglementaire : **la règle réelle est le minimum des deux**, quatre fois la hauteur de
référence sans jamais dépasser 30 mètres. Le référentiel ne portait que la seconde
moitié. Il était incomplet, et il a été corrigé en une journée.

**Le bureau d'études appliquait donc la bonne règle**, et aux hauteurs du dossier
c'étaient bien les valeurs proportionnelles qui s'imposaient, pas la borne de 30 mètres.

## Pourquoi c'est le pire type de lacune

La borne absolue est la partie de la règle qu'on retient. La partie proportionnelle est
celle qui **s'applique presque toujours** : dès que la hauteur de référence est
inférieure à 7,5 mètres, c'est elle qui contraint, et la borne de 30 mètres ne sert
jamais. Un référentiel qui ne retient que la borne absolue rate donc le cas le plus
courant, tout en ayant l'air de couvrir la règle.

Généralisation : **une règle composite retenue à moitié est plus dangereuse qu'une règle
absente.** Une règle absente produit un silence, qu'on remarque. Une règle à moitié
produit un verdict, qu'on croit.

Corollaire de constitution de référentiel : quand un texte énonce une valeur seuil,
chercher systématiquement s'il s'agit d'un minimum, d'un maximum, ou du plafond d'une
formule. Et vérifier quelle branche s'applique dans le domaine de valeurs réel du
métier, pas dans le cas limite.

## Ce que l'incertitude signalée a produit d'autre

La correction du référentiel n'a pas seulement rétabli la formule. En allant lire le
paragraphe manquant, deux exigences plus serrées sont apparues, qu'aucune des trois
passes humaines d'instruction n'avait relevées :

- la **hauteur de référence doit être chiffrée** dans la notice, ce qu'aucune pièce ne
  faisait ;
- un faux plafond n'est **neutralisé qu'à trois conditions cumulatives** (taux de
  passage libre supérieur à 50 %, ouvertures d'au moins 5 mm, plénum occupé à moins de
  50 %), chiffres à fournir. Faute de quoi la hauteur de référence se recalcule sous le
  faux plafond, et tout le calcul de distance est à refaire.

Une contradiction interne du dossier sur la nature des faux plafonds, déjà relevée par
ailleurs, avait donc une conséquence chiffrée sur l'implantation des équipements, et
pas seulement sur un point secondaire. **La lacune signalée a ouvert un point de
contrôle plus fort que celui qu'elle bouchait.**

## La règle de calcul de la précision, et elle est importante

Ce cas ne dégrade pas la précision mesurée du contrôle, et il faut savoir pourquoi.

Le constat initial disait : « cette formule n'est pas recoupable dans mon référentiel,
je ne peux ni la valider ni l'infirmer, et voici ce qui reste à corriger par ailleurs ».
Ce constat était **vrai au moment où il a été émis**, et il l'est resté après
vérification. Il ne passe donc pas de fondé à non fondé, et aucun chiffre du backtest
ne change.

Un constat qui aurait affirmé « cette formule n'existe pas » serait devenu faux, et
aurait dégradé la précision — et pire, aurait produit une demande de correction opposée
à tort à un tiers.

**C'est la différence entre un système calibré et un système confiant**, et elle est
mesurable exactement là : dans le sort d'un constat après vérification externe.

## Le comportement à valoriser, et comment on l'obtient

Un contrôle qui travaille sur un référentiel **fini** rencontrera nécessairement des
règles qu'il ne porte pas. La bonne conception ne cherche pas à éliminer ce cas, elle
cherche à le rendre visible.

Trois mécanismes concrets :

1. **Une sévérité dédiée à l'incertitude.** À côté de « bloquant » et « à corriger », un
   niveau « vigilance » ou « non recoupable » qui n'accuse rien et qui remonte. Sans ce
   niveau, le système est obligé de trancher, donc d'inventer.
2. **L'obligation de citer une référence.** Un constat qui doit nommer sa pièce et son
   article ne peut pas affirmer sans source : l'absence de référence devient visible dans
   le constat lui-même.
3. **Une relecture périodique des constats « non recoupables »** comme file de travail
   sur le référentiel. C'est la boucle qui fait grandir le référentiel là où il sert,
   plutôt que d'essayer de le rendre exhaustif d'avance.

## La règle générale

**Un système qui signale son incertitude au lieu d'affirmer rend ses lacunes
corrigeables en une journée. Un système confiant les rend invisibles jusqu'à ce qu'un
tiers les paie.**

Et la conséquence pour un backtest : ne pas compter comme erreur un constat qui déclare
honnêtement les limites de son référentiel. Le compter comme erreur, c'est entraîner le
système à affirmer.
