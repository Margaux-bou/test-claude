# Notes d'équipe — Ingénierie

## Processus : Revue de code
Chaque pull request doit être relue avant fusion.
Déclencheur: ouverture d'une pull request sur GitHub
Responsable: tech lead ou tout·e développeur·se senior
Outils: GitHub, Slack
Fréquence: à chaque pull request
Étapes:
1. L'auteur ouvre la PR et assigne au moins un reviewer
2. Le reviewer laisse ses commentaires dans les 24h
3. L'auteur adresse les commentaires ou justifie un désaccord
4. Une fois approuvée, l'auteur fusionne dans main

## Processus : Déploiement en production
Déclencheur: fusion sur la branche main
Responsable: équipe on-call
Outils: GitHub Actions, Datadog
Fréquence: quotidienne
Étapes:
1. La pipeline CI construit et teste l'artefact
2. Déploiement automatique en staging
3. Vérification manuelle des dashboards Datadog
4. Déploiement en production via approbation manuelle
5. Surveillance des alertes pendant 30 minutes
