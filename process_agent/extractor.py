"""Extraction des processus à partir des documents d'équipe.

Deux moteurs sont disponibles :

- ``ClaudeExtractor`` : utilise l'API Claude pour repérer des processus dans
  du texte libre et non structuré (messages Slack, comptes-rendus, tickets).
  C'est le moteur destiné à un usage réel.
- ``HeuristicExtractor`` : repli local, sans appel API, basé sur des
  motifs textuels simples (sections "## Processus : ...", listes d'étapes).
  Il permet de faire tourner le prototype de bout en bout sans clé API,
  par exemple en CI ou en démo.

``build_extractor`` choisit automatiquement le moteur Claude si
``ANTHROPIC_API_KEY`` est définie, sinon bascule sur l'heuristique.
"""

from __future__ import annotations

import json
import os
import re
from typing import Protocol

from .models import Document, ProcessRecord

SYSTEM_PROMPT = """Tu es un analyste qui identifie les processus de travail \
suivis par une équipe à partir d'un document interne (notes de réunion, \
documentation, ticket, message de chat, post-mortem...).

Un "processus" est une suite d'actions répétée par l'équipe pour atteindre \
un but récurrent (ex: revue de code, déploiement, onboarding, gestion \
d'incident, rétrospective...). Ignore les événements ponctuels qui ne se \
répètent pas.

Réponds UNIQUEMENT avec un tableau JSON (aucun texte autour), où chaque \
élément a la forme :
{
  "name": "nom court du processus",
  "description": "1-2 phrases décrivant son objectif",
  "trigger": "ce qui déclenche ce processus",
  "steps": ["étape 1", "étape 2", ...],
  "owner": "rôle ou personne responsable, si mentionné",
  "tools": ["outils/systèmes utilisés"],
  "frequency": "fréquence si mentionnée (ex: hebdomadaire, à chaque PR)"
}

Si le document ne décrit aucun processus, réponds avec un tableau vide [].
Laisse une valeur en chaîne vide "" ou tableau vide [] quand l'information \
n'est pas présente dans le document ; n'invente rien.
"""


class Extractor(Protocol):
    def extract(self, document: Document) -> list[ProcessRecord]: ...


class ClaudeExtractor:
    """Extraction par LLM (Claude) — pour du texte libre et non structuré."""

    def __init__(self, model: str = "claude-sonnet-4-5", client=None) -> None:
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self._client = client
        self._model = model

    def extract(self, document: Document) -> list[ProcessRecord]:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Document source: {document.source}\n\n{document.text}",
                }
            ],
        )
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        return _parse_llm_json(text, document.source)


def _parse_llm_json(text: str, source: str) -> list[ProcessRecord]:
    text = text.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        raw_items = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []

    records = []
    for item in raw_items:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        records.append(
            ProcessRecord(
                name=str(item.get("name", "")).strip(),
                description=str(item.get("description", "")).strip(),
                trigger=str(item.get("trigger", "")).strip(),
                steps=[str(s).strip() for s in item.get("steps", []) if str(s).strip()],
                owner=str(item.get("owner", "")).strip(),
                tools=[str(t).strip() for t in item.get("tools", []) if str(t).strip()],
                frequency=str(item.get("frequency", "")).strip(),
                confidence=0.8,
                sources=[source],
            )
        )
    return records


_SECTION_RE = re.compile(r"^#+\s*Processus\s*[:\-]\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_FIELD_RE = re.compile(
    r"^\s*[-*]?\s*(D[ée]clencheur|Responsable|Owner|Outils|Fr[ée]quence)\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)
_STEP_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.+)$")

_FIELD_MAP = {
    "déclencheur": "trigger",
    "declencheur": "trigger",
    "responsable": "owner",
    "owner": "owner",
    "outils": "tools",
    "fréquence": "frequency",
    "frequence": "frequency",
}


class HeuristicExtractor:
    """Repli local sans appel API, basé sur des motifs de mise en forme.

    Reconnaît des sections de la forme::

        ## Processus : Revue de code
        Déclencheur: ouverture d'une pull request
        Responsable: tech lead
        Outils: GitHub, Slack
        Fréquence: à chaque PR
        Étapes:
        1. ...
        2. ...
    """

    def extract(self, document: Document) -> list[ProcessRecord]:
        text = document.text
        headers = list(_SECTION_RE.finditer(text))
        if not headers:
            return []

        records = []
        for i, header in enumerate(headers):
            start = header.end()
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            block = text[start:end]
            record = self._parse_block(header.group(1).strip(), block, document.source)
            records.append(record)
        return records

    def _parse_block(self, name: str, block: str, source: str) -> ProcessRecord:
        record = ProcessRecord(name=name, confidence=0.6, sources=[source])
        description_lines = []
        steps: list[str] = []

        for line in block.splitlines():
            field_match = _FIELD_RE.match(line)
            step_match = _STEP_RE.match(line)
            stripped = line.strip()

            if field_match:
                key = _FIELD_MAP.get(field_match.group(1).lower(), None)
                value = field_match.group(2).strip()
                if key == "tools":
                    record.tools = [t.strip() for t in value.split(",") if t.strip()]
                elif key:
                    setattr(record, key, value)
            elif step_match:
                steps.append(step_match.group(1).strip())
            elif stripped and not stripped.lower().startswith(("étapes", "etapes")):
                description_lines.append(stripped)

        record.steps = steps
        record.description = " ".join(description_lines).strip()
        return record


def build_extractor(model: str = "claude-sonnet-4-5") -> Extractor:
    """Choisit automatiquement Claude si une clé API est disponible, sinon l'heuristique."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return ClaudeExtractor(model=model)
        except Exception:
            pass
    return HeuristicExtractor()
