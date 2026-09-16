"""Chargement des artefacts d'équipe depuis un dossier local.

Ce module ne fait aucune hypothèse sur la nature exacte des fichiers : il
charge tout fichier texte lisible (.md, .txt, .json) présent dans le dossier
donné. Dans un déploiement réel, on ajouterait ici des connecteurs dédiés
(export Slack, API Confluence/Notion, API Jira, `git log`, etc.) qui
produisent la même structure `Document` en sortie.
"""

from __future__ import annotations

from pathlib import Path

from .models import Document

SUPPORTED_SUFFIXES = {".md", ".txt", ".json"}


def load_documents(data_dir: str | Path) -> list[Document]:
    """Charge tous les documents supportés d'un dossier (récursivement)."""
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dossier introuvable: {root}")

    documents: list[Document] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                documents.append(Document(source=str(path.relative_to(root)), text=text))
    return documents
