# Post-mortem — Incident du 12 mars

## Processus : Gestion d'incident
Déclencheur: alerte Datadog ou signalement client
Responsable: ingénieur de garde (on-call)
Outils: PagerDuty, Slack #incidents, Datadog
Fréquence: à chaque incident de sévérité 1 ou 2
Étapes:
1. L'ingénieur de garde accuse réception de l'alerte dans PagerDuty
2. Création d'un canal Slack dédié #incident-YYYYMMDD
3. Diagnostic et mitigation immédiate
4. Communication de statut toutes les 30 minutes aux parties prenantes
5. Résolution puis rédaction d'un post-mortem dans les 48h
6. Revue du post-mortem lors de la rétrospective suivante

## Processus : Rétrospective d'équipe
Déclencheur: fin de sprint (toutes les deux semaines)
Responsable: scrum master
Outils: Miro, Google Meet
Fréquence: bi-hebdomadaire
Étapes:
1. Chacun note ce qui a bien fonctionné et ce qui peut être amélioré
2. Discussion collective des points soulevés
3. Sélection de 2-3 actions concrètes pour le prochain sprint
4. Suivi des actions lors de la rétrospective suivante
