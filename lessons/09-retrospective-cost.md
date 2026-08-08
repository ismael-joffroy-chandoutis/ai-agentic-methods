# Coût rétrospectif d'un dossier d'agents

Combien a réellement coûté un mois de travail conduit par des agents, machine et humain
séparés, et par quelle méthode le mesurer sans se raconter d'histoires.

## Ce qui est mesurable, et ce qui ne l'est pas

**Mesurable** : les jetons consommés, relevés dans les transcrits de session, avec pour
chaque événement **le nom du modèle réellement utilisé** — donc le prix de ce modèle,
jamais un prix moyen. Les durées d'audio, les nombres de messages et les volumes de
documents se mesurent sur les fichiers eux-mêmes.

**Non mesurable, et donc à déclarer absent des totaux** : les délégations à d'autres
fournisseurs (qui ne consomment pas les mêmes jetons), le calcul local (transcription,
diarisation : coût électrique, pas coût d'API — et c'est pourtant parfois le vrai coût
technique d'un livrable), les déplacements, les appels non enregistrés, et l'abonnement
lui-même, qui est la dépense réelle.

Un total honnête liste ses absences. Sinon il sert d'argument à des conclusions qu'il ne
porte pas.

## La méthode, en quatre étapes

1. **Extraction** : lire chaque transcrit de session en flux, sommer l'usage des
   événements assistant, appliquer le prix du modèle de chaque événement. Écriture de
   cache et lecture de cache ont leurs propres multiplicateurs et doivent être traitées
   séparément — on verra plus bas pourquoi c'est décisif.
2. **Attribution par blocs** : découper chaque session en blocs (une demande humaine et
   tout ce qu'elle déclenche), puis décider **bloc par bloc** si le travail relève du
   dossier mesuré.
3. **Agrégation par mission**, sur les dates et les fichiers touchés.
4. **Ventilation** par poste et par modèle.

### Le piège d'attribution, et il fausse tout d'un facteur trois

Dans un environnement où le nom du client apparaît dans les rappels système, l'index de
mémoire et les sorties de commandes, **presque toutes les sessions de la période le
mentionnent passivement**. Une première version du calcul, sans filtre, donnait
**trois fois trop**.

Il faut donc neutraliser les mentions passives avant l'attribution, sinon des journées
entièrement consacrées à d'autres sujets se retrouvent facturées au dossier.

### Deux bornes, jamais un chiffre unique

Comme l'attribution dans les sessions partagées est un **jugement, pas une mesure**, il
faut publier une fourchette et dire ce qui la définit :

- **borne large** : le bloc compte si la demande humaine porte sur le dossier **ou** si
  un outil a touché un de ses fichiers. Mesure tout ce qui a été consommé au service du
  dossier, orchestration partagée comprise.
- **borne stricte** : le bloc compte seulement si la demande humaine elle-même porte sur
  le dossier. Plus prudente, elle laisse de côté les relances techniques et les
  vérifications déclenchées automatiquement.

L'écart entre les deux bornes était ici d'environ 25 %. Chaque montant par mission doit
se lire avec une marge du même ordre.

Deux précautions supplémentaires : **dédoublonner par identifiant de message** (un même
échange apparaît dans plusieurs fichiers quand une session est reprise ou dupliquée), et
**horodater l'arrêt du relevé**, parce que la session en cours continue de produire.

## Le temps machine : une mesure, pas une durée d'horloge

Le temps machine actif est la somme des intervalles entre événements consécutifs d'un
même bloc, **plafonnés à 120 secondes**. Au-delà de deux minutes de silence, la machine
n'est plus en train de calculer, elle attend un humain : l'intervalle n'est pas compté.

L'étiqueter comme approximation, et dire ce qu'elle ne distingue pas (temps de
génération contre temps d'exécution d'outil).

**Le résultat le plus parlant du dossier tient dans une seule ligne** : une session
affichait 18,7 heures de machine active pour 12,1 heures d'horloge. Ce n'est pas une
erreur : les sous-agents tournaient en parallèle. **Une nuit de travail humain a mobilisé
une journée et demie de machine.** C'est exactement ce qu'un tel dispositif vend, et
c'est mesurable.

À l'échelle du dossier : 84 heures de machine active, 14 686 appels de modèle, sur des
sessions dont l'amplitude cumulée dépasse 1 100 heures (les sessions restent ouvertes
longtemps sans travailler — d'où l'inutilité de l'amplitude comme mesure).

## Le temps humain, en trois postes étiquetés séparément

C'est la partie que tout le monde bâcle, et c'est celle qui change la conclusion.
Trois postes, chacun avec sa méthode affichée :

**1. Temps devant les sessions (estimation).** Isoler les messages réellement écrits par
l'humain, en écartant les injections automatiques (notifications, sorties de commande,
rappels système) et les prompts de sous-agents, qui sont écrits par la machine. Puis
trois estimations convergentes avec des hypothèses différentes : dictée, frappe au
clavier, et somme des intervalles entre messages plafonnés. Sur ce dossier : de 5 à
16 heures selon l'hypothèse, valeur centrale autour de 8.

**2. Temps de lecture des livrables (estimation).** Compter les mots, hors doublons de
mise en forme, à une vitesse de lecture déclarée. Deux bornes : survol (résumé et
tableaux) et lecture intégrale. Ici : de 2,7 à 16,8 heures, avec une valeur de travail
retenue de 4 à 6 — parce que la plupart des documents ont été arbitrés sur leur résumé
et que certains n'ont jamais été ouverts. **Le dire est plus utile que de retenir la
borne haute.**

**3. Réunions, appels et échanges (factuel).** Durées relevées sur les fichiers audio, et
comptages de messages sur les bases locales de messagerie. C'est le seul poste qui n'est
pas une estimation.

### Le déséquilibre, qui est le vrai enseignement

| Poste | Fourchette | Valeur de travail |
|---|---|---|
| Devant les sessions | 5 à 16 h | 8 h |
| Lecture des livrables | 2,7 à 16,8 h | 5 h |
| Réunions, appels, messages | 14 à 17 h | 15 h |
| **Total** | **22 à 50 h** | **environ 28 h** |

**Le poste le plus lourd n'est pas la production, c'est la relation.** Quinze heures de
réunions et d'échanges contre huit heures de pilotage et cinq de lecture.

Et le rapport entre les 84 heures de machine et les 8 heures de présence est le vrai
indicateur du dispositif : **un facteur dix**.

## Trois découvertes structurelles qui se généralisent

**La moitié de la facture est de la relecture de contexte, pas de la production de
texte.** Les jetons de sortie pesaient environ 330 $, les jetons lus en cache environ
1 325 $. C'est le prix des documents longs relus à chaque itération et des contrôles
croisés. Conséquence : optimiser la longueur des sorties ne sert presque à rien ;
optimiser ce qu'on remet dans le contexte, beaucoup.

**La taille des fichiers ne dit rien du coût.** Le plus gros transcrit de la session
pesait 65 Mo et n'a coûté que 5,45 $, parce qu'une sortie d'outil de 15 Mo y a été
écrite sans jamais être renvoyée au modèle. **Toute estimation faite à partir du poids
des fichiers est fausse.**

**Le contrôle qualité coûte plus cher que la production.** Le chantier qui représentait
la moitié du coût de la session était le seul vérifié contre un étalon de corrections
humaines. C'est le prix des itérations et des contrôles croisés, et c'est un choix
assumé, pas une dérive.

Deux observations de ventilation par modèle, dans le même esprit : la désescalade vers
un modèle intermédiaire a bien fonctionné là où elle a été appliquée (14 % du volume
d'appels pour 5,3 % du coût, sur les mécaniques — conversions de fichiers, vérifications
de format, envois) ; et deux modèles au même tarif peuvent consommer très différemment,
l'un sur des passes longues à gros contexte, l'autre sur beaucoup d'appels courts.

## Ce que la mesure sert à décider

**Forfait pour la conception, usage pour le service.** Une facturation à l'usage aurait
rendu impossible la manière de travailler qui a produit ces livrables : relire un
document entier à chaque itération, lancer un contrôle adverse sur ses propres
conclusions, refaire un backtest contre un étalon humain. Ces gestes font la qualité, et
ce sont les plus coûteux en jetons. À l'inverse, en régime de service établi, un
livrable produit sur un contexte stable mis en cache coûte quelques dollars : coût
variable négligeable, mesurable, imputable client par client.

**Le coût de conception ne doit jamais servir de référence à un devis.** L'écart entre le
coût par livrable en phase de conception (avec ses essais et ses reprises) et le coût en
série est ici d'un **facteur vingt à trente**. C'est exactement la valeur du dispositif
construit — et c'est aussi le piège : facturer le service au prix de la conception, ou
l'inverse.

**La question qui décide de la rentabilité est la part réutilisable.** Elle se répond
poste par poste, pas globalement : référentiels et méthode presque intégralement
réutilisables, infrastructure produit intégralement, matière commerciale et juridique
intégralement, **données du client et travail spécifique sur son historique pas du
tout** — et c'est précisément ce que la mise en route facture. Ici, environ deux tiers de
la fabrication réutilisable. **Le modèle n'est pas dans la marge sur le premier client,
il est dans la pente de la courbe à partir du deuxième.**

## Le résultat le plus embarrassant, et il faut l'écrire

Le poste le plus lourd du temps humain était **une réunion fondatrice de huit heures,
enregistrée et jamais transcrite ni dépouillée**. Tout le dossier a été construit sans
elle, à partir des mails, des messages et d'appels ultérieurs.

Ce n'est pas du temps perdu — c'est ce qui a créé la relation. Mais c'est un actif
documentaire dormant : huit heures de matière première sur le besoin réel du client, pour
un coût de dépouillement de l'ordre de quelques dizaines d'euros en calcul local. C'est
probablement le meilleur rapport entre coût et valeur qui restait disponible sur le
dossier.

**Une mesure de coût sert aussi à ça : trouver ce qu'on possède et qu'on n'a pas
dépouillé.** Un gisement non exploité ne se distingue d'un trou que si on l'a mesuré.
