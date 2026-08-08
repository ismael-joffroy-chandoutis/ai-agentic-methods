# Scripts génériques

Cinq contrôles réutilisables, extraits d'un service de production de documents
conduit par des agents. Aucune configuration client ici : chaque script lit ses
règles dans un fichier externe.

| Script | Ce qu'il empêche | Leçon |
|---|---|---|
| [`output_gate.py`](output_gate.py) | Un livrable déclaré produit alors qu'il est absent, vide, illisible, trop court, ou qu'il porte des traces de fabrication | [04](../lessons/04-email-as-only-interface.md) |
| [`source_anchoring.py`](source_anchoring.py) | Un document qui cite une source jamais déposée | [02](../lessons/02-source-anchoring.md) |
| [`block_diff.py`](block_diff.py) | Une passe de correction qui n'a rien corrigé, ou qui modifie ce qu'on ne lui a pas demandé | [03](../lessons/03-transparent-correction-loop.md) |
| [`numeric_grounding.py`](numeric_grounding.py) | Un chiffre inventé dans une analyse rédigée | [06](../lessons/06-engine-agnosticism.md) |
| [`merge_findings.py`](merge_findings.py) | Un rapport de contrôle illisible : 118 constats bruts que personne ne lit | [01](../lessons/01-blind-backtest.md) |

## Dépendances

```
python3 -m pip install pyyaml python-pptx
```

`python-pptx` n'est requis que par les trois scripts qui ouvrent des documents
(`output_gate`, `source_anchoring`, `block_diff`). `numeric_grounding` et
`merge_findings` tournent sur la bibliothèque standard, `pyyaml` en plus pour
leurs options de règles.

## L'ordre dans lequel les brancher

Sur un livrable, dans une chaîne de production :

```
production  ->  output_gate  ->  source_anchoring  ->  livraison
                    |                   |
                    +-------------------+---> échec : mail d'excuse, jamais de silence
```

Sur une passe de correction, avant de livrer :

```
block_diff (passe N-1, passe N)
  |-- aucune différence dans la zone visée par la demande
  |     |-- la demande était déjà satisfaite -> le dire, ne pas consommer une passe
  |     +-- sinon -> échec de production
  +-- différences -> les lister dans le mail de livraison
```

`numeric_grounding` s'insère avant la mise en forme, sur la sortie structurée du
moteur, et sert aussi de juge dans une comparaison de moteurs.

`merge_findings` s'exécute après les contrôles thématiques, sur leurs constats
bruts.

## Deux principes qui traversent les cinq scripts

**Un code retour ne prouve rien.** Chaque script ouvre et mesure l'artefact réel.
Un contrôle qui ne trouve pas son vérificateur échoue au lieu de passer.

**Le déterminisme là où c'est possible.** Aucun de ces contrôles n'appelle un
modèle. Même entrée, même verdict, toujours, et sans coût variable. C'est ce qui
les rend opposables à un client et rejouables dans un test de non-régression.

## Licence

Code sous MIT (voir [`../LICENSE-CODE`](../LICENSE-CODE)). Les textes du dépôt
sont sous CC BY-SA 4.0.
