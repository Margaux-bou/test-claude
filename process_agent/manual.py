"""Processus déclarés manuellement par l'équipe (fichier JSON).

Certains processus ne sont décrits dans aucun document (accord tacite,
convention orale...) : ce module permet de les lister à la main et de les
assigner à des membres de l'équipe, au même format que ceux détectés
automatiquement. Ils sont ensuite fusionnés dans le même registre via
``ProcessRegistry`` (voir ``registry.py``).

Format attendu (liste de dictionnaires)::

    [
      {
        "name": "Astreinte de garde",
        "description": "...",
        "trigger": "...",
        "steps": ["...", "..."],
        "owner": "ingénieur de garde",
        "tools": ["PagerDuty"],
        "frequency": "hebdomadaire",
        "assignees": ["Léa Fontaine", "Karim Haddad"]
      }
    ]
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import ProcessRecord


def load_manual_processes(path: str | Path) -> list[ProcessRecord]:
    """Charge des processus déclarés à la main depuis un fichier JSON."""
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Le fichier de processus manuels doit contenir une liste JSON.")

    records = []
    for item in data:
        if not isinstance(item, dict) or not str(item.get("name", "")).strip():
            continue
        records.append(
            ProcessRecord(
                name=str(item["name"]).strip(),
                description=str(item.get("description", "")).strip(),
                trigger=str(item.get("trigger", "")).strip(),
                steps=[str(s).strip() for s in item.get("steps", []) if str(s).strip()],
                owner=str(item.get("owner", "")).strip(),
                tools=[str(t).strip() for t in item.get("tools", []) if str(t).strip()],
                frequency=str(item.get("frequency", "")).strip(),
                assignees=[str(a).strip() for a in item.get("assignees", []) if str(a).strip()],
                confidence=1.0,
                sources=[str(item.get("source", "")).strip() or file_path.name],
            )
        )
    return records
