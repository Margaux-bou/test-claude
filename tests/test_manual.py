from process_agent.manual import load_manual_processes
from process_agent.registry import ProcessRegistry


def test_load_manual_processes_reads_assignees():
    records = load_manual_processes("data/manual_processes.json")
    names = {r.name for r in records}

    assert "Astreinte de garde" in names
    assert "Revue trimestrielle des accès" in names

    astreinte = next(r for r in records if r.name == "Astreinte de garde")
    assert astreinte.confidence == 1.0
    assert "Léa Fontaine" in astreinte.assignees
    assert astreinte.sources == ["manual_processes.json"]


def test_registry_merges_assignees_across_sources():
    from process_agent.models import ProcessRecord

    registry = ProcessRegistry()
    registry.add(ProcessRecord(name="Revue de code", assignees=["Léa Fontaine"], sources=["a.md"]))
    registry.add(ProcessRecord(name="Revue de code", assignees=["Karim Haddad"], sources=["b.md"]))

    merged = registry.all()[0]
    assert set(merged.assignees) == {"Léa Fontaine", "Karim Haddad"}
