import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from rag.vector_store import clinical_store
from rag.knowledge_docs import CLINICAL_DOCUMENTS

def test_clinical_documents_loaded():
    """Verify documents are present and well-structured."""
    assert len(CLINICAL_DOCUMENTS) >= 8
    for doc in CLINICAL_DOCUMENTS:
        assert "id" in doc
        assert "category" in doc
        assert "title" in doc
        assert "content" in doc
        assert len(doc["content"]) > 100

def test_cbt_search():
    """Verify CBT queries retrieve relevant CBT cognitive restructuring docs."""
    results = clinical_store.search("I keep catastrophizing and thinking everything is a disaster", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert "catastrophiz" in top_doc["content"].lower() or "cbt" in top_doc["category"].lower()
    assert top_doc["relevance_score"] > 0.1

def test_grounding_search():
    """Verify panic and grounding queries retrieve 5-4-3-2-1 / breathing methods."""
    results = clinical_store.search("I am having a panic attack please help me ground myself", top_k=2)
    assert len(results) > 0
    categories = [r["category"] for r in results]
    assert "grounding" in categories or "dbt" in categories

def test_crisis_lifeline_search():
    """Verify crisis query retrieves 988 emergency lifeline information."""
    results = clinical_store.search("suicide hotline crisis helpline", category="crisis", top_k=1)
    assert len(results) == 1
    assert "988" in results[0]["content"]

def test_category_filtering():
    """Verify category filtering strictly filters non-matching categories."""
    results = clinical_store.search("breathing and emotions", category="dbt", top_k=3)
    for doc in results:
        assert doc["category"] == "dbt"

def test_clinical_context_formatting():
    """Verify formatted context block string."""
    context = clinical_store.get_clinical_context("anxiety and thought reframing")
    assert isinstance(context, str)
    assert "[Clinical Resource:" in context
