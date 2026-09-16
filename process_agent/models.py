"""Structures de données partagées par l'agent."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Document:
    """Un artefact d'équipe à analyser (note, doc, ticket, message...)."""

    source: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessRecord:
    """Un processus identifié dans un ou plusieurs documents."""

    name: str
    description: str = ""
    trigger: str = ""
    steps: list[str] = field(default_factory=list)
    owner: str = ""
    tools: list[str] = field(default_factory=list)
    frequency: str = ""
    confidence: float = 0.5
    sources: list[str] = field(default_factory=list)

    def key(self) -> str:
        """Clé normalisée utilisée pour rapprocher deux mentions du même processus."""
        return " ".join(self.name.lower().split())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def merge(self, other: "ProcessRecord") -> "ProcessRecord":
        """Fusionne deux mentions du même processus (venant de documents différents)."""
        merged_steps = self.steps or other.steps
        if other.steps and other.steps != self.steps:
            for step in other.steps:
                if step not in merged_steps:
                    merged_steps.append(step)

        merged_tools = list(dict.fromkeys(self.tools + other.tools))
        merged_sources = list(dict.fromkeys(self.sources + other.sources))

        return ProcessRecord(
            name=self.name,
            description=self.description or other.description,
            trigger=self.trigger or other.trigger,
            steps=merged_steps,
            owner=self.owner or other.owner,
            tools=merged_tools,
            frequency=self.frequency or other.frequency,
            confidence=max(self.confidence, other.confidence),
            sources=merged_sources,
        )
