"""Point d'entrée CLI de l'agent d'identification de processus.

Exemple::

    python -m process_agent.cli --data-dir data/samples --output report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .extractor import ClaudeExtractor, HeuristicExtractor, build_extractor
from .ingest import load_documents
from .registry import ProcessRegistry
from .report import to_html, to_json, to_markdown


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Identifie les processus suivis par une équipe à partir de ses documents."
    )
    parser.add_argument(
        "--data-dir",
        default="data/samples",
        help="Dossier contenant les documents d'équipe (.md, .txt, .json). Défaut: data/samples",
    )
    parser.add_argument(
        "--output",
        default="processes_report.md",
        help="Fichier Markdown de sortie. Défaut: processes_report.md",
    )
    parser.add_argument(
        "--json-output",
        default=None,
        help="Fichier JSON optionnel contenant le registre structuré.",
    )
    parser.add_argument(
        "--html-output",
        default=None,
        help="Fichier HTML optionnel : tableau de bord interactif (recherche, filtres, étapes).",
    )
    parser.add_argument(
        "--team-label",
        default="Équipe",
        help="Nom affiché dans le tableau de bord HTML (ex: 'Équipe Ingénierie').",
    )
    parser.add_argument(
        "--engine",
        choices=["auto", "claude", "heuristic"],
        default="auto",
        help="Moteur d'extraction. 'auto' utilise Claude si ANTHROPIC_API_KEY est définie.",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5",
        help="Modèle Claude à utiliser (si engine=claude ou auto avec clé API).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.engine == "claude":
        extractor = ClaudeExtractor(model=args.model)
    elif args.engine == "heuristic":
        extractor = HeuristicExtractor()
    else:
        extractor = build_extractor(model=args.model)

    print(f"[process-agent] Moteur d'extraction: {type(extractor).__name__}", file=sys.stderr)

    documents = load_documents(args.data_dir)
    print(f"[process-agent] {len(documents)} document(s) chargé(s) depuis {args.data_dir}", file=sys.stderr)

    registry = ProcessRegistry()
    for document in documents:
        try:
            records = extractor.extract(document)
        except Exception as exc:  # pragma: no cover - dépend d'un service externe
            print(f"[process-agent] Échec sur {document.source}: {exc}", file=sys.stderr)
            continue
        registry.add_all(records)
        print(f"[process-agent]   {document.source}: {len(records)} processus détecté(s)", file=sys.stderr)

    results = registry.all()

    Path(args.output).write_text(to_markdown(results), encoding="utf-8")
    print(f"[process-agent] Rapport écrit dans {args.output}", file=sys.stderr)

    if args.json_output:
        Path(args.json_output).write_text(to_json(results), encoding="utf-8")
        print(f"[process-agent] Registre JSON écrit dans {args.json_output}", file=sys.stderr)

    if args.html_output:
        Path(args.html_output).write_text(to_html(results, team_label=args.team_label), encoding="utf-8")
        print(f"[process-agent] Tableau de bord HTML écrit dans {args.html_output}", file=sys.stderr)

    print(f"\n{len(results)} processus identifié(s) au total.")
    for record in results:
        print(f"- {record.name} ({len(record.sources)} source(s))")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
