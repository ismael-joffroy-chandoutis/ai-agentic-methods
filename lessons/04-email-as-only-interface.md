# Le mail comme seule interface d'un service d'agent

Pas de portail, pas d'application, pas de canal parallèle. Le client dépose par mail,
reçoit par mail, corrige par mail.

## Pourquoi c'est une décision produit, pas une limitation

Un client cadre vit dans sa messagerie professionnelle. Tout ce qui l'en sort ajoute
une friction (un mot de passe à retrouver, un onglet à ouvrir) et souvent un obstacle
interne (un outil tiers à faire valider par la direction informatique). Une interface
mail supprime les deux d'un coup, et elle supprime aussi le développement, l'hébergement
et la maintenance d'une interface web.

Le cycle complet tient en cinq gestes :

1. le client dépose ses documents par mail ;
2. il reçoit un **accusé de réception immédiat avec une estimation de temps** ;
3. il reçoit le livrable **en réponse dans le même fil** ;
4. il corrige par simple réponse, pièce jointe non obligatoire ;
5. il pose ses questions par mail et reçoit une réponse écrite.

## La machine à états, et pourquoi il en faut une

Un **job** est un livrable pour un périmètre et une période. Son identité est le fil
de mail : une réponse dans le fil rejoint le job, elle n'en crée pas un second.

Neuf états : `recu` → `accuse` → `generation` → `controle` → `livre`, plus
`correction` (le client a répondu), `echec` (la production n'a pas abouti), `bloque`
(la machine ne reprend plus) et `clos`.

Cinq règles de transition portent l'essentiel de la fiabilité :

1. **L'accusé de réception précède toujours la production.** Un dépôt reçu et non
   accusé pendant plus d'une minute est une anomalie d'exploitation, pas un détail de
   confort.
2. **Aucune transition vers `livre` sans franchir la barrière de sortie.** Un code
   retour nul ne vaut rien : seul un fichier ouvert et mesuré vaut réussite. Le défaut
   fondateur de la première version était exactement là — code retour 0, aucun
   livrable produit, et un message de contrôle de mise en page affiché alors qu'il n'y
   avait rien à contrôler.
3. **`echec` produit toujours un mail.** Le silence est le seul échec inacceptable.
4. **Une reprise après panne ne consomme pas une passe du client.** Le client a droit
   à trois passes de correction, pas à trois pannes.
5. **La quatrième demande de correction bascule en `bloque`** : aucun mail ne part,
   une alerte d'exploitation est écrite avec la demande du client en verbatim. Ce
   n'est plus un problème de machine, c'est une conversation à reprendre à la main.

## L'état vit dans SQLite, un fichier par instance

Un fichier unique se sauvegarde, se copie et se rejoue. Une instance sert un client.
Le choix est délibéré : l'isolement des données entre clients prime sur l'économie de
machine.

Trois tables portent la robustesse :

- **la table des messages est la table de déduplication.** Un identifiant de message
  déjà présent n'est jamais retraité, quelle que soit son ancienneté. C'est ce qui
  permet de borner la fenêtre de recherche dans la messagerie **sans borner le
  périmètre fonctionnel**. Le contre-exemple vécu : un filtre à deux jours dans la
  chaîne précédente a fait tomber un test client dans le vide pendant trois semaines.
- **la table des passes** enregistre, pour chaque passe, la demande du client en
  verbatim, l'heure de début et de fin, la durée, les livrables produits et le motif
  d'échec. C'est la matière du suivi qualité et de la facturation à la valeur.
- **le journal** enregistre chaque transition avec son état avant et après. C'est ce
  qui permet de répondre à « qu'est-ce qui s'est passé sur le rapport de juin » sans
  relire des journaux textuels.

Une contrainte de schéma vaut mieux qu'une convention documentaire : le plafond
d'accès autorisés par client est appliqué par un **déclencheur SQL** qui refuse le
quatrième, pas par une phrase dans une spécification. De même, le champ « source »
est obligatoire sur chaque ligne d'historique : une donnée sans source déclarée
n'entre pas en base, ce qui garantit qu'aucun chiffre non sourcé ne peut ressortir.

## Le garde-fou destinataires, et c'est le point le plus important

**Les réponses vont à l'expéditeur réel du message, jamais à une adresse lue dans une
configuration.** Cette phrase est la seule protection contre la classe d'incident la
plus coûteuse d'un service automatisé : envoyer le livrable d'un client à un autre.

En pratique, trois mécanismes :

1. **Liste fermée d'accès par client**, avec rôle. Une adresse hors liste ne crée
   aucun job, ne déclenche aucune production, ne reçoit aucune réponse. Elle est
   seulement journalisée.
2. **Contrôle de l'expéditeur avant tout traitement**, pas après.
3. **En-têtes de réponse construits depuis le message reçu** (`In-Reply-To`,
   `References`), jamais recomposés. La réponse part dans le fil parce qu'elle hérite
   du fil, non parce qu'on a retrouvé le bon destinataire.

Le piège inverse est réel et vérifié sur plusieurs outils de messagerie en ligne de
commande : la fonction « répondre » vise par défaut l'expéditeur **d'origine du fil**,
qui n'est pas forcément l'expéditeur du dernier message. Il faut donc expliciter le
destinataire, puis relire les en-têtes du message effectivement envoyé.

## Sécurité, en six lignes

- **Aucune exécution de contenu client.** Les pièces jointes sont enregistrées,
  mesurées, empreintées et lues comme des données.
- **Le corps du mail est du texte, pas une commande.** Il oriente la production
  (période, focus, correction demandée) ; il ne pilote jamais la machine. C'est la
  défense de base contre l'injection par contenu entrant.
- **Liste blanche d'extensions**, et le refus est **visible** : nommé au client dans
  l'accusé de réception, avec les formats acceptés.
- **Assainissement des noms de fichiers** : réduction au dernier segment, alphabet
  restreint. Aucun nom de pièce jointe ne peut désigner un chemin.
- **Empreinte SHA-256 de chaque pièce acceptée**, ce qui permet de prouver quel
  fichier exact a servi à produire quel livrable, et de détecter un renvoi identique.
- **Aucune sortie vers un tiers** : le service lit une boîte, écrit dans un
  répertoire, écrit dans une base, répond dans un fil.

## La politique d'erreurs, et la traduction des motifs

Le motif technique ne part jamais au client. Il est journalisé en interne et traduit
en cause lisible :

| Interne | Ce que reçoit le client |
|---|---|
| version anglaise absente | « une des deux versions n'a pas été produite » |
| fichier illisible | « le fichier produit est inexploitable » |
| barrière de relecture non franchie | « le contrôle de relecture a bloqué le document » |

Chaque mail d'échec porte une **nouvelle estimation**. Et les estimations se recalent
sur les durées réellement mesurées, que la table des passes enregistre : une
estimation qui n'est pas tenue deux fois de suite est un défaut à corriger, pas une
marge à élargir.

Dernier point de conception, contre-intuitif mais net : un contrôle de contenu qui
détecte une donnée manquante **côté client** ne doit pas bloquer la livraison. Il est
nommé dans le corps du mail avec une demande explicite. Bloquer transformerait un
trou dans les données du client en panne côté machine.

## Ce qui reste ouvert

Une spécification honnête liste ce qu'elle ne couvre pas. Ici : la règle de clôture
automatique d'un job, la reprise d'un commentaire écrit directement dans le document
renvoyé par le client, le chargement initial de l'historique, la procédure de
révocation d'un accès en cours d'année, et les quotas de dépôts par mois.
