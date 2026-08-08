# Répéter le déploiement en conteneur avant d'acheter le serveur

Une procédure d'installation écrite n'est pas une procédure d'installation testée.
Celle-ci s'arrêtait au bout de 85 secondes.

## Le banc d'essai

Un conteneur Debian avec **systemd réellement en PID 1**, sur une machine déjà
disponible. Ce point n'est pas cosmétique : c'est ce qui permet d'exercer les unités,
les minuteries, le confinement des services et le journal, c'est-à-dire précisément la
partie de la procédure que personne n'avait jamais exécutée.

Tout le travail vit dans le conteneur et dans un volume dédié. Rien d'existant sur la
machine hôte n'est modifié.

## Ce que la répétition a trouvé

Huit écarts, dont cinq auraient bloqué la vraie machine, plus une illusion de
sécurité. Les deux plus coûteux d'abord.

**Le service ne pouvait pas démarrer.** L'unité systemd lançait un module Python qui
n'existait pas, et **aucune étape de la procédure n'installait le code du service sur
la machine** : l'étape de préparation clonait le dépôt puis n'en copiait que le
fichier de dépendances. Signal obtenu : `ModuleNotFoundError`. Correction : point
d'entrée en variable, pointé par défaut sur la chaîne réellement éprouvée, plus un
avertissement explicite si le code n'est pas là.

**La minuterie partait avant tout contrôle.** Le script d'installation terminait par
`systemctl enable --now`, ce qui démarre la boucle immédiatement, alors que les secrets
ne sont pas déposés et que l'essai à vide (décrit dans la procédure comme le point de
contrôle le plus important de la journée) n'a pas eu lieu. Résultat mesuré : échec du
service toutes les cinq minutes. Et une fois l'alerte sur échec posée à l'étape
suivante, cela produit **une alerte toutes les cinq minutes**. Correction : `enable`
sans `--now`, démarrage explicite reporté après l'essai à vide.

Les six autres, en une ligne chacun :

| Écart | Correction |
|---|---|
| `openssh-server` absent de la liste de paquets, et son répertoire de configuration supposé existant | paquet ajouté, répertoire créé explicitement |
| `systemctl reload ssh` **recharge sans valider**, et tue le script si le service n'est pas déjà actif | `sshd -t` avant tout rechargement, puis rechargement ou démarrage selon l'état |
| `sqlite3` absent de la liste de paquets, alors que toute la machine à états y vit | paquet ajouté |
| installation des dépendances sur un fichier que rien ne garantit, produisant une erreur illisible | contrôle explicite en tête, message qui renvoie à l'étape fautive, arrêt propre |
| le script de sauvegarde lit un fichier d'environnement créé plus tard, dans un répertoire que personne ne crée | répertoire créé en 0700, contrôle de lisibilité, sortie en erreur avec un message qui dit quoi faire |
| les scripts appellent `python3` **par le PATH**, donc le Python système, qui n'a pas les dépendances installées dans l'environnement dédié | `PATH` de l'unité préfixé par l'environnement dédié |

**L'écart le plus dangereux du lot est le second**, et il mérite d'être isolé : une
faute de frappe dans un fichier de durcissement SSH, rechargée sans contrôle, coupe
l'accès au serveur. `sshd -t` avant tout `reload` est une ligne, et c'est la
différence entre une correction et un déplacement chez l'hébergeur.

## Le neuvième point : une unité concrète qui masque l'unité modèle

Ce n'est pas une correction, c'est une illusion à ne pas garder. L'unité portait :

```
ExecStartPre=/usr/bin/flock -n ${BASE}/${CENTRE}/.verrou true
```

présenté en commentaire comme le verrou qui garantit « une seule exécution à la fois ».
Ce n'est pas ce qu'il fait. `flock -n <fichier> true` acquiert le verrou, exécute
`true`, et le relâche aussitôt : le verrou est relâché **avant** que `ExecStart` ne
démarre.

Mesuré sur la machine, la sérialisation réelle vient d'ailleurs, et elle fonctionne :

- **systemd** fusionne deux démarrages simultanés d'un service `Type=oneshot` en une
  seule tâche. Deux `systemctl start` en parallèle donnent un seul démarrage dans le
  journal, un seul job en base, aucun identifiant de message en doublon ;
- **le service** tient son propre verrou. Neuf lancements en rafale : un seul produit
  un job, huit sont refusés.

L'exigence est donc satisfaite, mais par deux mécanismes autres que celui que le
commentaire désigne. **Le commentaire promet plus que le code ne tient**, et c'est
exactement le genre de ligne qu'on reprendrait comme acquise dans un audit.

Leçon transposable : quand une unité modèle (`service@.service`) et une unité concrète
coexistent, ou quand un garde-fou est documenté à côté du code qui ne le porte pas,
la vérification consiste à **provoquer la collision** et à lire le journal, pas à
relire la configuration.

## L'idempotence, affirmée en tête du script et jamais éprouvée

| Mesure | Résultat |
|---|---|
| Reconstruction complète d'une machine vierge, après correction | **88 s**, dont 85 d'installation de paquets |
| Relance du même script sur la même machine | **2 s**, aucun changement d'état |

Après relance : aucun compte dupliqué, permissions inchangées (répertoires en 700,
fichier de secrets en 600), minuteries toujours activées et toujours non démarrées,
aucune unité en échec. L'affirmation tient — mais elle ne tenait qu'après les huit
corrections, et personne n'en savait rien avant de mesurer.

## Ce qu'un conteneur ne peut pas tester, et qu'il faut déclarer

Un banc d'essai honnête liste ses angles morts, sinon il donne une fausse assurance :

- **volume chiffré et déverrouillage distant au démarrage** : pas de disque secondaire
  ni d'initramfs dans un conteneur. C'est le seul bloc entier de la procédure qui
  reste sur parole ;
- **voie d'envoi du courrier** : authentification du domaine, en-têtes
  d'authentification sur un message réellement reçu. Rien envoyé, par consigne ;
- **sauvegarde vers un stockage objet distant** : la mécanique de sauvegarde, de
  rotation et de restauration est validée localement (restauration vérifiée par un
  diff vide) ; les identifiants et la latence réseau restent à valider ;
- **comportement du pare-feu sous adressage public** : la syntaxe, le chargement et
  l'activation au démarrage ont pu être vérifiés, le comportement réel non ;
- **architecture processeur** différente de la cible : à contrôler au premier passage.

Et un point qui vaut d'être noté parce qu'il est facile à manquer : un contrôle de
sortie qui **se dégrade proprement mais silencieusement** (« contrôle non exécuté,
vérificateur introuvable ») laisse passer des livrables sans contrôle sans que
personne ne s'en aperçoive. Une dégradation propre doit rester bruyante.

## Ce que le chronométrage a réellement appris

Le budget de la journée d'installation n'est pas à réviser à la baisse, mais sa
structure change : **le temps machine est négligeable, la totalité du budget est du
temps humain.** Ouvrir des comptes, saisir des identifiants, choisir des phrases de
passe, lire des journaux, décider.

Deux conséquences pratiques. D'abord, la condition de réussite n'est pas technique :
sans les moyens de paiement, les comptes et les identifiants prêts **avant** de
commencer, la journée devient deux jours. Ensuite, il faut retirer du budget le temps
de débogage que les huit écarts auraient consommé — trouver seul qu'un module n'existe
pas, que la minuterie tourne dans le vide et que l'interpréteur système n'a pas les
dépendances, sur une machine distante, en fin de journée, ce n'est pas une demi-heure.

## La règle générale

**Répéter le déploiement sur un banc jetable coûte quelques heures et transforme une
procédure écrite en procédure éprouvée.** Le conteneur doit reproduire ce qui compte
(systemd en PID 1, comptes confinés, unités et minuteries réelles), pas simuler le
service.

Et le verdict d'une répétition n'est pas « prêt » ou « pas prêt » : c'est une liste
courte de pièces à fournir, séparée de la liste des inconnues techniques restantes.
Les deux ne se traitent pas au même moment ni par les mêmes personnes.
