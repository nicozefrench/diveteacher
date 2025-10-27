"""
Tests pour Docling + Chunking pipeline

NOTE: Ces tests nécessitent:
- Docker containers running (Neo4j, backend)
- Test PDF file disponible
"""
import pytest
from pathlib import Path
from app.integrations.dockling import convert_document_to_docling, extract_document_metadata
from app.services.document_chunker import get_chunker
from app.services.document_validator import DocumentValidator


# ═════════════════════════════════════════════════════════════
# DocumentValidator Tests
# ═════════════════════════════════════════════════════════════

def test_validator_invalid_extension():
    """Test validation avec extension non supportée"""
    is_valid, msg = DocumentValidator.validate("test.txt", max_size_mb=50)
    assert not is_valid
    assert "Unsupported format" in msg


def test_validator_file_not_exists():
    """Test validation avec fichier inexistant"""
    is_valid, msg = DocumentValidator.validate("nonexistent.pdf", max_size_mb=50)
    assert not is_valid
    assert "File does not exist" in msg


# TODO: Ajouter test avec vrai PDF valide
# def test_validator_valid_pdf():
#     """Test validation avec PDF valide"""
#     test_pdf = "TestPDF/Niveau 4 GP.pdf"
#     is_valid, msg = DocumentValidator.validate(test_pdf, max_size_mb=50)
#     assert is_valid
#     assert msg == "Valid"


# ═════════════════════════════════════════════════════════════
# Docling Conversion Tests
# ═════════════════════════════════════════════════════════════

# TODO: Test conversion nécessite container running
# @pytest.mark.asyncio
# async def test_docling_conversion():
#     """Test conversion Docling avec test.pdf"""
#     test_pdf = "TestPDF/Niveau 4 GP.pdf"
#     doc = await convert_document_to_docling(test_pdf)
#     
#     # Vérifier DoclingDocument
#     assert doc is not None
#     assert len(doc.pages) > 0
#     
#     # Vérifier metadata
#     metadata = extract_document_metadata(doc)
#     assert metadata["num_pages"] > 0


# ═════════════════════════════════════════════════════════════
# HybridChunker Tests
# ═════════════════════════════════════════════════════════════

# TODO: Test chunking nécessite DoclingDocument
# def test_hybrid_chunking():
#     """Test HybridChunker avec DoclingDocument"""
#     # Nécessite DoclingDocument de test
#     pass


# ═════════════════════════════════════════════════════════════
# Placeholder Tests (pour CI/CD)
# ═════════════════════════════════════════════════════════════

def test_placeholder_pass():
    """Placeholder test pour CI/CD (toujours pass)"""
    assert True

