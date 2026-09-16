"""Génération d'un rapport lisible à partir des processus identifiés."""

from __future__ import annotations

import json

from .models import ProcessRecord


def to_json(records: list[ProcessRecord]) -> str:
    return json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2)


def to_markdown(records: list[ProcessRecord]) -> str:
    lines = ["# Processus identifiés dans l'équipe", ""]

    if not records:
        lines.append("Aucun processus n'a été identifié dans les documents fournis.")
        return "\n".join(lines)

    lines.append(f"{len(records)} processus identifié(s).")
    lines.append("")
    lines.append("| Processus | Responsable | Déclencheur | Fréquence | Sources |")
    lines.append("|---|---|---|---|---|")
    for record in records:
        lines.append(
            "| {name} | {owner} | {trigger} | {frequency} | {sources} |".format(
                name=record.name,
                owner=record.owner or "—",
                trigger=record.trigger or "—",
                frequency=record.frequency or "—",
                sources=", ".join(record.sources) or "—",
            )
        )
    lines.append("")

    for record in records:
        lines.append(f"## {record.name}")
        if record.description:
            lines.append(record.description)
        lines.append("")
        if record.trigger:
            lines.append(f"- **Déclencheur** : {record.trigger}")
        if record.owner:
            lines.append(f"- **Responsable** : {record.owner}")
        if record.frequency:
            lines.append(f"- **Fréquence** : {record.frequency}")
        if record.tools:
            lines.append(f"- **Outils** : {', '.join(record.tools)}")
        lines.append(f"- **Sources** : {', '.join(record.sources)}")
        lines.append(f"- **Confiance** : {record.confidence:.0%}")
        if record.steps:
            lines.append("")
            lines.append("**Étapes :**")
            for i, step in enumerate(record.steps, start=1):
                lines.append(f"{i}. {step}")
        lines.append("")

    return "\n".join(lines)
