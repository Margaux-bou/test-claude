# Process Identification Agent (prototype)

Prototype d'agent qui analyse les artefacts d'une équipe (notes de réunion,
documentation interne, tickets, extraits de chat...) pour **identifier les
processus réellement en vigueur** : revue de code, gestion d'incident,
onboarding, déploiement, rétrospective, etc.

## Idée générale

1. **Ingestion** (`process_agent/ingest.py`) : lit tous les fichiers texte
   (`.md`, `.txt`, `.json`) d'un dossier. Dans un déploiement réel, on
   brancherait ici des connecteurs vers Slack, Confluence/Notion, Jira,
   `git log`, etc. — chacun produit des `Document` avec la même structure.
2. **Extraction** (`process_agent/extractor.py`) : pour chaque document, un
   moteur repère les processus décrits.
   - `ClaudeExtractor` : utilise l'API Claude pour comprendre du texte
     libre et non structuré (c'est le mode destiné à un usage réel).
   - `HeuristicExtractor` : repli 100% local, sans clé API, basé sur des
     motifs de mise en forme (`## Processus : ...`). Sert de démo et de
     filet de secours.
   - `build_extractor()` choisit automatiquement Claude si
     `ANTHROPIC_API_KEY` est définie, sinon l'heuristique.
3. **Consolidation** (`process_agent/registry.py`) : un même processus
   apparaît souvent dans plusieurs documents avec un nom légèrement
   différent ("revue de code" mentionné dans 3 fichiers). Le registre
   regroupe les mentions similaires et fusionne leurs informations
   (déclencheur, étapes, outils, responsable, sources).
4. **Processus manuels** (`process_agent/manual.py`) : certains processus ne
   sont décrits dans aucun document (convention orale, accord tacite...).
   Ce module les charge depuis un fichier JSON et les assigne à des membres
   de l'équipe, au même format que ceux détectés automatiquement — voir
   `data/manual_processes.json`.
5. **Rapport** (`process_agent/report.py`) : génère un rapport Markdown
   (tableau récapitulatif + fiche détaillée par processus), un export JSON
   structuré exploitable par un autre outil, et un **tableau de bord HTML
   interactif** autonome (recherche, filtres, étapes dépliables, indicateur
   de confiance) qui permet en plus, directement dans le navigateur,
   d'**ajouter manuellement de nouveaux processus** et de **gérer leur
   assignation à des membres de l'équipe** (persisté dans ce navigateur).

## Utilisation

```bash
pip install -r requirements.txt

# Sans clé API : bascule automatiquement sur le moteur heuristique local
python -m process_agent.cli --data-dir data/samples --output processes_report.md

# Avec l'API Claude (extraction plus fine sur du texte libre), en ajoutant
# les processus manuels et le trombinoscope de l'équipe
export ANTHROPIC_API_KEY=sk-...
python -m process_agent.cli --data-dir data/samples \
  --manual-file data/manual_processes.json \
  --roster-file data/team_roster.json \
  --output processes_report.md \
  --json-output processes.json \
  --html-output dashboard.html --team-label "Équipe Ingénierie"
```

Ouvrez ensuite `dashboard.html` dans un navigateur pour explorer les
processus identifiés (recherche, filtres, détail des étapes, indicateur de
confiance) — vous pouvez aussi y **ajouter un nouveau processus à la main**
et **l'assigner à un ou plusieurs membres de l'équipe** (bouton « + Nouveau
processus », et « Gérer l'assignation » sur chaque fiche). Ces ajouts sont
conservés dans le navigateur (`localStorage`) tant que vous ne videz pas
ses données.

Options utiles :

- `--engine {auto,claude,heuristic}` : force un moteur en particulier.
- `--model` : modèle Claude à utiliser (défaut `claude-sonnet-4-5`).
- `--json-output` : écrit aussi le registre structuré en JSON.
- `--html-output` / `--team-label` : génère le tableau de bord HTML
  interactif, avec le nom d'équipe affiché en en-tête.
- `--manual-file` : fusionne des processus déclarés à la main (avec leurs
  membres assignés) — voir `data/manual_processes.json`.
- `--roster-file` : liste de membres à proposer dans les assignations même
  s'ils ne sont, pour l'instant, assignés à aucun processus — voir
  `data/team_roster.json`.

## Données d'exemple

`data/samples/` contient des artefacts fictifs représentatifs d'une équipe
produit/ingénierie : workflow de dev, post-mortem d'incident, doc
d'onboarding et un extrait de chat Slack non structuré. Ils permettent de
faire tourner le prototype de bout en bout sans données réelles.

Remplacez ce dossier par vos propres exports (Slack, Confluence, Jira...)
pour analyser les processus de votre propre équipe.

## Limites du prototype

- L'ingestion se limite à des fichiers texte locaux ; les connecteurs vers
  des outils tiers (API Slack, Jira, Confluence) restent à écrire.
- Le moteur heuristique ne reconnaît qu'un format de section précis ; il
  sert de démo, la qualité d'extraction sur du texte vraiment libre dépend
  du moteur Claude.
- Aucune persistance côté serveur : chaque exécution du CLI repart de
  zéro à partir des documents et fichiers manuels fournis. Les ajouts faits
  dans le tableau de bord HTML ne sont sauvegardés que dans le navigateur
  qui les a créés (`localStorage`) — un usage en équipe nécessiterait un
  stockage partagé (base de données, fichier versionné...).

## Tests

```bash
python -m pytest tests/
```
