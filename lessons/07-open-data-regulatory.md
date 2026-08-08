# Open data française pour un contrôle réglementaire

Ce qu'une machine peut aller chercher toute seule pour instruire un dossier, et les
trois endroits où elle se trompe avec l'assurance d'une base nationale.

Toutes les sources ci-dessous ont été testées en réel, sans clé quand elles sont
ouvertes. Aucune n'est citée sur la foi de sa documentation.

## Le piège à lire avant tout le reste : le géocodage par adresse postale

**Il invalide silencieusement toute requête géographique, et c'est le pire des cas :
aucune erreur ne remonte.**

Le premier réflexe est de géocoder un site par son adresse postale. La Base Adresse
Nationale répond proprement, avec un score de confiance élevé sur une adresse exacte.
**Le point peut être faux de plus d'un kilomètre.**

Sur le cas testé, un grand centre commercial : le point retourné tombait en centre-ville.
Interrogé sur ce point, le Géoportail de l'Urbanisme répondait un zonage
parfaitement cohérent, parfaitement vérifiable — et sans aucun rapport avec le site
visé. Toute la chaîne répondait juste sur le mauvais objet.

L'erreur a été détectée **par recoupement, pas par relecture** : la base nationale des
bâtiments donnait, comme plus grande emprise de la commune, un bâtiment situé
ailleurs. Le géocodage inverse de ce centroïde a tranché : **le centre possède sa
propre voie dans la Base Adresse Nationale**, dont le libellé n'est pas celui de
l'avenue de son adresse postale. Vérification dans l'autre sens : une recherche par
nom commercial renvoyait encore un troisième lieu.

**Règle à graver dans le système** : ne jamais géocoder un grand équipement par son
adresse postale. Partir de l'emprise bâtie ou de la référence de parcelle, et
**contrôler le résultat par géocodage inverse** avant d'interroger quoi que ce soit
d'autre. Quelques lignes de code, et cela élimine une classe entière d'erreurs
silencieuses.

## Le référentiel qui se surveille lui-même : Légifrance via PISTE

**C'est la source la plus structurante**, parce qu'elle transforme un référentiel
réglementaire figé en document qui se surveille au lieu de vieillir en silence.

L'API Légifrance est exposée par la DILA via la plateforme d'API de l'État. Elle
remplace un scraping fragile par un accès officiel et versionné aux textes consolidés.
Le flux : compte sur le portail, application déclarée, souscription à l'API, jeton
obtenu en `client_credentials` par OAuth, puis appels sur l'hôte de production.

Deux clients libres (un en Python, un en JavaScript) documentent le flux et évitent de
réécrire l'authentification.

**Ce que le système en tire** : mise à jour et surveillance automatiques des textes du
référentiel, citation fiable, et surtout **traçabilité de la date du droit appliqué**.
C'est ce qui empêche un référentiel de rendre un avis fondé sur un texte abrogé.

Pendant urbanisme du même mécanisme : le Géoportail de l'Urbanisme expose un **flux
Atom de ses publications récentes**, testé et à jour à l'heure de la requête. Il permet
de détecter qu'un document d'urbanisme a été modifié sans repasser à la main.

## Le contexte opposable, gratuit et sans clé : API Carto

À partir d'une seule référence de parcelle contrôlée, l'API Carto (module Géoportail de
l'Urbanisme) rend, en réponses immédiates et sans clé :

- le **document d'urbanisme opposable** avec son identifiant et sa date d'approbation ;
- le **zonage** au point ;
- les **prescriptions** applicables (orientations d'aménagement, par exemple) ;
- les **informations surfaciques**, qui sont l'apport le plus utile.

Sur le premier essai, deux des cinq informations trouvées **déclenchaient une procédure
distincte** de l'autorisation instruite : un secteur soumis à permis de démolir, et un
règlement local de publicité. Les manquer ne produit pas un dossier imparfait, mais un
chantier illégal.

**Ce que le système en fait** : produire automatiquement, en tête de chaque relecture,
un encadré « contexte d'urbanisme opposable » qui nomme le document applicable et sa
date, le zonage, et la liste des servitudes qui déclenchent une procédure parallèle.
Aujourd'hui cette information est soit absente du contrôle, soit ressaisie à la main
dossier après dossier.

## Le règlement local qui nomme les sites : le RLPi

Le règlement local de publicité intercommunal signalé par l'API a été retrouvé et
téléchargé. Découverte qui change la nature du contrôle : **le zonage du règlement
nomme explicitement les sites concernés**, centre commercial par centre commercial, dans
la définition de ses zones.

Il n'y a donc aucune interprétation à faire. Les règles d'enseigne applicables sont
celles de la zone qui cite le site, et elles sont chiffrées : surface maximale des
enseignes perpendiculaires et leur saillie, part maximale de la surface vitrée,
surface maximale d'une enseigne numérique, dispositifs d'éclairage interdits et
autorisés, saillie maximale des dispositifs, interdictions (clignotant, mouvant,
défilant, animé, luminosité variable, bâche, structure gonflable).

**Ces valeurs deviennent des points de contrôle mécaniques sans aucun développement.**
Et une conséquence à signaler au preneur : un aménagement avec enseigne conduit
**trois procédures parallèles** (autorisation de travaux, autorisation préalable
d'enseigne, et le cas échéant déclaration préalable ou permis), dont aucune ne dispense
des deux autres.

Généralisation : les documents locaux d'urbanisme et de publicité sont des PDF, donc
invisibles pour une chaîne qui n'interroge que des API. Ce sont pourtant eux qui
portent les valeurs chiffrées directement opposables. **Il faut les récupérer et les
dépouiller une fois**, pas les redécouvrir à chaque dossier.

## La base nationale des bâtiments : utile, mais à ne pas croire sur parole

API ouverte, sans clé. Fiche complète d'un groupe de bâtiments : 138 champs.

**Ce qui est fiable et vaut d'être utilisé** : l'identification et la délimitation du
bâtiment — emprise au sol, centroïde, identifiant stable. C'est exactement le service
qui a permis de détecter l'erreur de géocodage ci-dessus.

**Ce qui est faux et dangereux** : sur le cas testé, le champ **année de construction**
donnait 2019 pour un ensemble ouvert au début des années 1970 et plusieurs fois
étendu. C'est un artefact de données dérivées, probablement rattaché à une extension
récente prise pour l'ensemble du groupe.

Ce n'est pas une anecdote, c'est un avertissement de portée générale. L'année de
construction est précisément le critère qui départage, en accessibilité, le cadre bâti
existant et la construction neuve — donc le texte applicable. **Une chaîne automatisée
qui irait chercher là son critère produirait une réponse fausse, avec l'assurance d'une
base nationale.**

De même, hauteur moyenne et nombre de niveaux sont des moyennes sur une emprise
hétérogène de plusieurs hectares. Elles ne peuvent pas servir de hauteur de référence
pour un calcul de désenfumage, où l'erreur se paie immédiatement (voir
[la leçon sur le référentiel incomplet](08-signal-uncertainty.md)).

**Pour tout le reste que l'identification du bâti, cette base sert à formuler une
question, pas à y répondre.**

## Le résultat négatif le plus utile : il n'existe pas de registre ERP public

Recherche menée sur le portail national de données ouvertes : aucun registre national
des établissements recevant du public, aucun avis de commission de sécurité publié.
L'organisation du service d'incendie compétent y possède une page et **n'y publie aucun
jeu de données** — constat obtenu par une voie totalement indépendante d'un premier
constat identique sur l'absence de doctrine publiée.

Et c'est cohérent avec les textes : le guide départemental impose au maire d'établir
annuellement la liste des ERP de sa commune et de la transmettre au service qui tient
la base départementale. **Cette base existe, elle est nominative, et elle n'est pas
ouverte.** Ce n'est pas un oubli de publication : le registre est un outil de police
administrative.

**Ce que le système doit en conclure** : renoncer à tout pré-remplissage automatique
depuis un registre ERP public, et considérer le référentiel du bailleur comme la seule
base de connaissance exploitable sur les locaux. **C'est une contrainte
d'architecture, pas un détail.** La liste des établissements se demande au client,
pas à une API.

Leçon de méthode : un résultat négatif documenté vaut une source. Il évite de
construire une brique sur une donnée qui n'existe pas, et il se cite dans un dossier.

## Synthèse

| Source | Testée | Ce que le système en tire |
|---|---|---|
| API Légifrance / PISTE | endpoint vérifié vivant | mise à jour et surveillance des textes, traçabilité de la date du droit appliqué |
| API Carto (urbanisme) | oui, sans clé | encadré « urbanisme opposable » par parcelle, déclencheurs de procédure parallèle |
| Flux Atom du Géoportail | oui, à jour | alerte sur modification du document d'urbanisme |
| Règlement local de publicité | oui, téléchargé et dépouillé | points de contrôle enseignes chiffrés, procédure supplémentaire à signaler |
| API Carto (cadastre) | oui, sans clé | identifiant de parcelle stable, clé d'entrée de toutes les autres requêtes |
| Base Adresse Nationale | oui, dans les deux sens | géocodage **et surtout** contrôle inverse obligatoire |
| Portail de données ouvertes | oui | résultat négatif utile : pas de registre ERP, pas d'avis publiés |
| Base nationale des bâtiments | oui | emprise et identifiant fiables ; **année de construction et hauteur à ne pas utiliser** |

**Ordre de mise en œuvre**, du meilleur rapport valeur sur effort au moins bon :

1. **contrôle de géocodage inverse** avant toute requête géographique ;
2. **encadré urbanisme opposable** par API Carto, à partir de la parcelle ;
3. **points de contrôle enseignes** issus du règlement local, valeurs déjà chiffrées ;
4. **inscription à la plateforme d'API de l'État et surveillance des textes** : effort
   réel, valeur la plus durable ;
5. **flux Atom** en veille passive ;
6. **base des bâtiments** en dernier, pour l'identification du bâti seulement.

## Ce que l'open data ne résout pas

Aucune source ouverte ne donne accès à ce qui manque vraiment au contrôle : la doctrine
locale d'assimilation d'une activité atypique à un type réglementaire, la trame de
notice attendue par la sous-commission compétente, les valeurs de dimensionnement des
normes payantes, le cahier des charges technique du bailleur, la configuration réelle
des installations du site.

**L'open data enrichit le contexte et automatise la veille réglementaire. Il ne
remplace aucune des questions qu'il faut poser par écrit.**
