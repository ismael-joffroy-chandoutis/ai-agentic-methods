# Harness QC multi-agents

Comment vérifier ce que des agents produisent, sans faire confiance à leurs résumés.

## Règle de base
Un agent qui dit avoir écrit un fichier n'a rien prouvé : il peut décrire un fichier
jamais écrit. Contrôle mécanique après chaque étape d'écriture (liste des fichiers attendus,
taille, contenu) avant d'enchaîner.

## Pattern
1. **Canon** : une source de vérité unique (faits, nommage, contraintes de style) partagée.
2. **Audit par document** : un agent par document, en parallèle, qui liste chaque écart
   au canon (erreur factuelle, incohérence, contradiction interne, manque, ton, typo),
   avec citation exacte et correction.
3. **Cohérence croisée** : vérifier que les documents ne se contredisent pas entre eux
   (mêmes chiffres, mêmes noms, mêmes prix).
4. **Verify adversarial** : pour toute affirmation forte, des vérificateurs indépendants
   cherchent à la réfuter. Un gain de métrique est suspect jusqu'à preuve.
5. **Application** : corriger, republier, revérifier.

## Pourquoi
Le résumé d'un agent n'est pas une preuve. Le signal frais observé sur l'artefact réel, si.
