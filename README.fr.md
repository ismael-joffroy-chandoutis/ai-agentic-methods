[English](README.md) · **Français**

# Agentic methods

Méthodes réutilisables pour construire des systèmes d'agents IA qui produisent
des livrables lisibles. Aucune donnée client ici : ce sont des méthodes, pas des cas.

## Méthodes

- **[GEO / AEO audit](geo-aeo-audit-method.md)** : mesurer et améliorer la visibilité
  d'une marque dans les réponses des IA (ChatGPT, Gemini, Perplexity, Google AI Overviews).
- **[Reporting agentique](agentic-reporting-method.md)** : structurer un reporting mensuel
  qui se produit seul à partir de documents déposés.
- **[Harness QC multi-agents](multi-agent-qc-harness.md)** : vérifier de façon adversariale
  ce que des agents produisent, avec un contrôleur-rattrapeur après chaque écriture.

## Neuf leçons d'une nuit de travail agentique

Un service documentaire conduit par des agents, mené en une nuit du prototype au
déploiement répété : un contrôle réglementaire validé à l'aveugle contre trois passes
de relecture humaine, une boucle de correction par mail testée en conditions réelles,
un déploiement serveur répété en conteneur avant d'acheter la machine, la même tâche
exécutée sur quatre moteurs de raisonnement, et une mesure rétrospective du coût
complet du dossier. Tout est anonymisé : ce qui se généralise est la méthode, jamais
le cas.

1. **[Backtest à l'aveugle](lessons/01-blind-backtest.md)** — valider un contrôle
   documentaire automatisé contre des corrections humaines qu'il n'a jamais vues :
   71 % de rappel strict, 99,2 % de précision, et pourquoi les ratés ne sont jamais
   réglementaires.
2. **[Barrière d'ancrage des sources](lessons/02-source-anchoring.md)** — un rapport
   généré citait une source jamais déposée, et la barrière de sortie ne l'a pas vue.
   Le contrôle en liste fermée qui ferme la porte.
3. **[Boucle de correction transparente](lessons/03-transparent-correction-loop.md)** —
   annoncer une correction n'est pas la prouver : diff de blocs entre passes, refus de
   livrer quand la zone visée n'a pas bougé, et réponse honnête au cas « déjà
   satisfait ».
4. **[Le mail comme seule interface](lessons/04-email-as-only-interface.md)** — pas de
   portail, pas d'application : machine à états, SQLite comme registre, plafond de
   passes, et le garde-fou destinataires qui répond à l'expéditeur réel plutôt qu'à
   une configuration.
5. **[Répéter le déploiement en conteneur](lessons/05-rehearse-deployment-in-container.md)**
   — systemd réellement en PID 1, huit écarts bloquants trouvés avant de dépenser un
   euro d'hébergement, et un verrou qui promettait plus qu'il ne tenait.
6. **[Agnosticisme moteur](lessons/06-engine-agnosticism.md)** — la même tâche sur
   quatre moteurs de quatre familles, dont un modèle local à poids ouverts : ce que ça
   prouve, ce que ça ne prouve pas, et pourquoi la production appelle l'API HTTP et
   non le CLI agentique (facteur d'environ 300 sur le coût).
7. **[Open data française pour un contrôle réglementaire](lessons/07-open-data-regulatory.md)**
   — le piège du géocodage par adresse postale, qui répond juste sur le mauvais
   bâtiment, la mise à jour automatique d'un référentiel de textes, et les trois
   champs d'une base nationale à ne pas croire.
8. **[Un référentiel incomplet, et l'incertitude signalée](lessons/08-signal-uncertainty.md)**
   — la moitié d'une règle composite est plus dangereuse qu'une règle absente, et un
   contrôle qui signale son incertitude rend la lacune corrigeable en une journée.
9. **[Coût rétrospectif d'un dossier d'agents](lessons/09-retrospective-cost.md)** —
   mesurer séparément le temps machine et le temps humain : 84 heures de machine
   contre 8 heures de présence, la moitié de la facture en relecture de contexte, et
   le poids des fichiers qui ne dit rien du coût.

## Code générique

Cinq contrôles réutilisables et déterministes dans [`code/`](code/) — barrière de
sortie, ancrage des sources, diff de blocs, ancrage numérique, fusion de constats.
Aucun n'appelle de modèle : même entrée, même verdict, toujours.

## Licence

Textes : CC BY-SA 4.0 ([LICENSE](LICENSE)). Code : MIT ([LICENSE-CODE](LICENSE-CODE)).
Par Ismaël Joffroy Chandoutis.
