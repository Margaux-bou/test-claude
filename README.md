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
4. **Rapport** (`process_agent/report.py`) : génère un rapport Markdown
   (tableau récapitulatif + fiche détaillée par processus), un export JSON
   structuré exploitable par un autre outil, et un **tableau de bord HTML
   interactif** autonome (recherche, filtre par responsable, étapes
   dépliables, indicateur de confiance) — voir capture ci-dessous.

## Utilisation

```bash
pip install -r requirements.txt

# Sans clé API : bascule automatiquement sur le moteur heuristique local
python -m process_agent.cli --data-dir data/samples --output processes_report.md

# Avec l'API Claude (extraction plus fine sur du texte libre)
export ANTHROPIC_API_KEY=sk-...
python -m process_agent.cli --data-dir data/samples \
  --output processes_report.md \
  --json-output processes.json \
  --html-output dashboard.html --team-label "Équipe Ingénierie"
```

Ouvrez ensuite `dashboard.html` dans un navigateur pour explorer les
processus identifiés (recherche, filtre par responsable, détail des
étapes, indicateur de confiance).

Options utiles :

- `--engine {auto,claude,heuristic}` : force un moteur en particulier.
- `--model` : modèle Claude à utiliser (défaut `claude-sonnet-4-5`).
- `--json-output` : écrit aussi le registre structuré en JSON.
- `--html-output` / `--team-label` : génère le tableau de bord HTML
  interactif, avec le nom d'équipe affiché en en-tête.

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
- Aucune persistance : chaque exécution repart de zéro. Un usage continu
  nécessiterait de stocker le registre (base de données) et de ne
  ré-analyser que les nouveaux documents.

## Tests

```bash
python -m pytest tests/
```
