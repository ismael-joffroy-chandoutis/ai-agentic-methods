# Agnosticisme moteur : le démontrer, pas l'affirmer

« Si votre fournisseur d'IA disparaît demain, que devient notre service ? » La bonne
réponse n'est pas une note d'architecture, c'est la même tâche exécutée sur quatre
moteurs.

## Le découpage qui rend la question soluble

Un service de production de documents se décompose en cinq briques. **Une seule est un
moteur de raisonnement.**

| Brique | Ce qu'elle fait | Dépend d'un fournisseur ? |
|---|---|---|
| Chaîne de traitement | relever la boîte, comprendre la demande, identifier le périmètre, produire, mettre en forme, répondre dans le bon fil, gérer les erreurs, reprendre sans doublon | non |
| Règles métier | ce qu'on montre, ce qu'on ne montre pas, comparaisons interdites, cadrage imposé, angles proscrits | non (fichiers versionnés, lisibles) |
| Contrôles | tout ce qui empêche un chiffre faux de partir | non (c'est du code) |
| Socle de données | historique, gabarits validés, mémoire des livrables précédents | non (fichiers, chez le client) |
| **Moteur de raisonnement** | transformer des chiffres et des règles en analyse rédigée | oui |

La conséquence est directe : changer de fournisseur de moteur ne touche ni la chaîne,
ni les règles, ni les contrôles, ni les données. C'est un remplacement de pièce.

Le contrôle décisif, en particulier, n'est pas un moteur. C'est un script qui **extrait
toutes les valeurs numériques d'une sortie et vérifie leur présence dans les données
d'entrée** : [`code/numeric_grounding.py`](../code/numeric_grounding.py). Il ne dépend
d'aucun fournisseur, et c'est lui qui attrape le chiffre inventé.

## La démonstration

Même tâche métier, même paquet d'entrée, mêmes consignes, **même contrôle de sortie**,
sur quatre moteurs de quatre familles différentes : deux moteurs propriétaires de deux
éditeurs, un troisième d'un éditeur distinct, et un modèle à poids ouverts de 27
milliards de paramètres tournant sur une machine locale, appelé par son interface HTTP,
sans qu'aucune donnée ne sorte du réseau.

**Les quatre ont produit un résultat exploitable et conforme au format demandé.**

Ce qui rend la démonstration valide n'est pas le nombre de moteurs, c'est que
l'entrée, les règles et **le validateur** soient strictement identiques pour tous. Le
validateur est le juge : sans lui, quatre sorties différentes ne prouvent rien.

## Ce que le modèle local sait faire, et ce qu'il rate

C'est le résultat le plus utile de l'exercice, parce qu'il est contre-intuitif dans les
deux sens.

**Ce qu'il fait correctement** : il respecte le schéma JSON au caractère près, n'invente
aucun chiffre, applique les règles de qualification, tient la langue, produit les
tableaux exacts. Il formule même l'observation la plus fine des quatre sorties, absente
des trois autres.

**Ce qu'il rate, et c'est net : l'analyse causale.** Il attribue l'écart du mois à deux
événements survenus dans les derniers jours du mois, qui ne peuvent arithmétiquement
pas l'expliquer. La cause réelle, un événement structurel antérieur, est identifiée par
les trois moteurs propriétaires et absente de sa sortie.

D'où un partage de tâches qui n'est pas un principe mais une conclusion :

| Étape | Où elle tourne | Donnée exposée à un tiers |
|---|---|---|
| Extraction des chiffres | sur site | aucune |
| Classification, normalisation | sur site | aucune |
| Mise en forme, remplissage du gabarit | sur site | aucune |
| Contrôles de sortie | sur site, par du code | aucune |
| Analyse rédigée, hiérarchisation des causes | moteur frontière, ou sur site en mode dégradé | agrégats seulement |
| Relecture finale | humain | sans objet |

Une seule étape sur six appelle un moteur externe, et elle peut être alimentée par des
agrégats plutôt que par la donnée détaillée. En mode entièrement souverain, cette
étape bascule aussi sur site, au prix d'une analyse moins fine qui demande une
relecture plus attentive. **C'est un curseur, pas un interrupteur.**

Ordre de grandeur matériel pour la version souveraine : 24 à 32 Go de mémoire
graphique (un modèle de 27 à 35 milliards de paramètres quantisé en occupe 17 à 23),
32 Go de mémoire vive, 1 To de stockage. Système indifférent, l'appel se fait en HTTP.
Investissement unique, sans coût variable ensuite.

## Le piège d'appel qui fausse tout : CLI agentique contre API HTTP

Deux constats indépendants, et ils vont dans le même sens.

**Le texte est corrompu.** Le modèle local appelé par son outil interactif renvoie du
texte pollué par des séquences d'échappement de terminal. Le même modèle appelé par
son interface HTTP renvoie du JSON propre. Une évaluation menée par le CLI aurait
conclu à tort que le modèle ne tient pas le format.

**Le coût explose.** Un moteur frontière appelé par son CLI agentique consomme le
contexte de l'outil, ses instructions système, ses définitions d'outils et ses
allers-retours, là où un appel API direct n'envoie que la tâche. Sur cette
tâche-ci, le rapport est de l'ordre d'un **facteur 300**.

Règle qui en sort : **le CLI agentique est un outil de développement et d'exploration ;
en production, on appelle l'API HTTP.** Confondre les deux fausse à la fois la mesure
de qualité et l'estimation de coût, dans des directions opposées.

## L'état honnête de l'abstraction

C'est la partie qu'il faut écrire avec le plus de soin, parce que c'est celle qu'une
démonstration en salle démentirait.

**Ce qui existe** : un point d'appel unique dans la chaîne de production. L'orchestrateur
ne connaît qu'une seule manière de produire un livrable, la commande déclarée sous une
clé du fichier de configuration. Toute la mécanique autour (verrou, transcription des
consignes, barrière de sortie, livraison, message d'excuse) est indifférente à ce qui
se trouve derrière cette clé. C'est le **prérequis** d'un sélecteur, et il est là : il
n'y a pas d'appel de moteur dispersé dans le code.

**Ce qui n'existe pas** : le sélecteur lui-même. Il n'y a pas de variable qu'on
positionnerait à tel ou tel fournisseur pour basculer. Écrire que le service est déjà
commutable serait faux.

**Ce qu'il faudrait**, sans mystère : une variable de configuration `moteur` ; un
adaptateur par famille, une trentaine de lignes chacun (construire l'appel, envoyer,
récupérer le texte, extraire le JSON, remonter jetons et durée) ; un jeu de contrôle de
non-régression, c'est-à-dire quelques mois de données réelles avec leurs sorties
attendues, à rejouer après tout changement ; et une journalisation du moteur utilisé
pour chaque livrable, afin qu'un écart de qualité soit rattachable.

Quelques jours de travail d'interface. Ce n'est pas un chantier structurant, et il n'a
pas à être fait avant qu'il serve. **Le dire est plus utile au dossier que de laisser
croire à un système déjà commutable.**

## Ce qu'un standard de format ne résout pas

Un format ouvert de description de composants d'agents (compétences et connecteurs)
apporte la réversibilité du **format des règles métier**. Il ne définit aucune
interface d'appel de moteur, et ne rend donc aucun moteur interchangeable.

L'indépendance vis-à-vis du moteur ne vient pas du standard. Elle vient du découpage en
cinq briques et se démontre par l'expérience. Confondre les deux est une erreur
d'argumentaire fréquente et facile à démonter en réunion.

## Ce que la démonstration ne prouve pas

- **Quatre exécutions ne sont pas une mesure.** Un choix de moteur en production
  demanderait une dizaine d'exécutions par moteur sur plusieurs mois de données, avec
  relecture humaine. La démonstration établit la faisabilité, pas un classement.
- **Le mois testé était particulier**, structuré par un événement antérieur qui met les
  moteurs à l'épreuve sur la hiérarchisation des causes. Un cas plus ordinaire les
  discriminerait probablement moins.
