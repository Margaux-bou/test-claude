from process_agent.ingest import load_documents


def test_load_documents_reads_sample_dir():
    documents = load_documents("data/samples")
    sources = {doc.source for doc in documents}

    assert "dev_workflow.md" in sources
    assert "chat_excerpt.txt" in sources
    assert all(doc.text for doc in documents)


def test_load_documents_missing_dir_raises():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_documents("data/does_not_exist")
