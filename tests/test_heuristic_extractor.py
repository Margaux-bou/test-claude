from process_agent.extractor import HeuristicExtractor
from process_agent.ingest import load_documents
from process_agent.registry import ProcessRegistry


def test_heuristic_extractor_parses_process_sections():
    documents = load_documents("data/samples")
    dev_workflow = next(d for d in documents if d.source == "dev_workflow.md")

    records = HeuristicExtractor().extract(dev_workflow)
    names = {r.name for r in records}

    assert "Revue de code" in names
    assert "Déploiement en production" in names

    review = next(r for r in records if r.name == "Revue de code")
    assert review.owner == "tech lead ou tout·e développeur·se senior"
    assert "GitHub" in review.tools
    assert len(review.steps) == 4


def test_registry_merges_duplicate_processes_across_documents():
    documents = load_documents("data/samples")
    extractor = HeuristicExtractor()
    registry = ProcessRegistry()

    for document in documents:
        registry.add_all(extractor.extract(document))

    results = {r.name: r for r in registry.all()}

    assert "Revue de code" in results
    review = results["Revue de code"]
    assert len(review.sources) >= 2
