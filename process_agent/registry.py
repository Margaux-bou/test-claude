"""Consolidation des processus détectés dans plusieurs documents.

Un même processus (ex: "revue de code") peut être mentionné dans plusieurs
documents avec des libellés légèrement différents. Ce module regroupe les
mentions par nom normalisé, puis fusionne leurs informations.
"""

from __future__ import annotations

from difflib import SequenceMatcher

from .models import ProcessRecord

SIMILARITY_THRESHOLD = 0.82


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


class ProcessRegistry:
    """Accumule des ``ProcessRecord`` et fusionne les doublons au fil de l'eau."""

    def __init__(self) -> None:
        self._records: list[ProcessRecord] = []

    def add_all(self, records: list[ProcessRecord]) -> None:
        for record in records:
            self.add(record)

    def add(self, record: ProcessRecord) -> None:
        for i, existing in enumerate(self._records):
            if _similarity(existing.key(), record.key()) >= SIMILARITY_THRESHOLD:
                self._records[i] = existing.merge(record)
                return
        self._records.append(record)

    def all(self) -> list[ProcessRecord]:
        return sorted(self._records, key=lambda r: (-len(r.sources), r.name.lower()))
