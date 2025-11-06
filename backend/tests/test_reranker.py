"""
Unit Tests for Cross-Encoder Reranker Module

Tests the CrossEncoderReranker class to ensure correct functionality
of the reranking system.

Author: DiveTeacher Team
Date: November 4, 2025
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.reranker import CrossEncoderReranker, get_reranker


class TestCrossEncoderReranker:
    """Test suite for CrossEncoderReranker class"""
    
    def test_model_loads_successfully(self):
        """Test that the cross-encoder model loads without errors"""
        reranker = CrossEncoderReranker()
        assert reranker.model is not None
        assert reranker.model_name == 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    
    def test_rerank_with_sufficient_facts(self):
        """Test reranking with more facts than top_k"""
        reranker = CrossEncoderReranker()
        
        # Create test facts
        facts = [
            {"fact": "Equipment maintenance is important", "id": 1},
            {"fact": "Diving safety procedures are critical", "id": 2},
            {"fact": "Underwater navigation techniques", "id": 3},
            {"fact": "Marine life identification", "id": 4},
            {"fact": "Decompression sickness prevention", "id": 5},
            {"fact": "Emergency procedures for divers", "id": 6},
            {"fact": "Buddy system in diving", "id": 7},
            {"fact": "Dive planning essentials", "id": 8},
            {"fact": "Equipment check procedures", "id": 9},
            {"fact": "Post-dive safety checks", "id": 10}
        ]
        
        query = "What are the safety procedures for diving?"
        
        # Rerank to top 5
        result = reranker.rerank(query, facts, top_k=5)
        
        # Assertions
        assert len(result) == 5
        assert all(isinstance(fact, dict) for fact in result)
        assert all("fact" in fact for fact in result)
        
        # Safety-related facts should rank higher
        # (exact order may vary, but safety keywords should be prominent)
        result_texts = [f["fact"] for f in result]
        assert any("safety" in text.lower() or "procedures" in text.lower() 
                   for text in result_texts[:3])  # At least one in top 3
    
    def test_rerank_with_insufficient_facts(self):
        """Test reranking when len(facts) <= top_k (no reranking needed)"""
        reranker = CrossEncoderReranker()
        
        facts = [
            {"fact": "Equipment check", "id": 1},
            {"fact": "Safety first", "id": 2},
            {"fact": "Buddy system", "id": 3}
        ]
        
        query = "diving safety"
        
        # Request top 5, but only 3 facts available
        result = reranker.rerank(query, facts, top_k=5)
        
        # Should return all 3 facts without reranking
        assert len(result) == 3
        assert result == facts[:3]
    
    def test_rerank_with_empty_facts(self):
        """Test reranking with empty facts list"""
        reranker = CrossEncoderReranker()
        
        result = reranker.rerank("test query", [], top_k=5)
        
        assert result == []
    
    def test_rerank_with_empty_fact_text(self):
        """Test reranking when some facts have empty text"""
        reranker = CrossEncoderReranker()
        
        facts = [
            {"fact": "Valid fact 1", "id": 1},
            {"fact": "", "id": 2},  # Empty fact
            {"fact": "Valid fact 2", "id": 3}
        ]
        
        query = "test query"
        
        # Should handle gracefully
        result = reranker.rerank(query, facts, top_k=2)
        
        assert len(result) == 2
        assert all(isinstance(fact, dict) for fact in result)
    
    def test_rerank_performance(self):
        """Test reranking performance is within acceptable limits"""
        import time
        
        reranker = CrossEncoderReranker()
        
        # Create 20 facts
        facts = [{"fact": f"Test fact number {i}", "id": i} for i in range(20)]
        
        query = "test query"
        
        start_time = time.time()
        result = reranker.rerank(query, facts, top_k=5)
        duration = time.time() - start_time
        
        # Should complete in < 500ms (plan specifies ~100ms, but being conservative)
        assert duration < 0.5
        assert len(result) == 5
    
    def test_rerank_returns_top_k_correctly(self):
        """Test that reranking returns exactly top_k results"""
        reranker = CrossEncoderReranker()
        
        facts = [{"fact": f"Fact {i}", "id": i} for i in range(10)]
        
        for top_k in [1, 3, 5, 7]:
            result = reranker.rerank("test", facts, top_k=top_k)
            assert len(result) == top_k
    
    def test_rerank_preserves_fact_structure(self):
        """Test that reranking preserves the structure of fact dictionaries"""
        reranker = CrossEncoderReranker()
        
        facts = [
            {"fact": "Test 1", "id": 1, "source": "doc1", "metadata": {"key": "value"}},
            {"fact": "Test 2", "id": 2, "source": "doc2", "metadata": {"key": "value2"}},
            {"fact": "Test 3", "id": 3, "source": "doc3", "metadata": {"key": "value3"}}
        ]
        
        result = reranker.rerank("test", facts, top_k=2)
        
        # Check all original keys are preserved
        assert all("fact" in fact for fact in result)
        assert all("id" in fact for fact in result)
        assert all("source" in fact for fact in result)
        assert all("metadata" in fact for fact in result)
    
    @patch('app.core.reranker.CrossEncoder')
    def test_rerank_fallback_on_error(self, mock_cross_encoder):
        """Test that reranking falls back to original order on error"""
        # Mock the model to raise an exception
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Test error")
        mock_cross_encoder.return_value = mock_model
        
        reranker = CrossEncoderReranker()
        reranker.model = mock_model
        
        facts = [{"fact": f"Fact {i}", "id": i} for i in range(10)]
        
        # Should fall back to original order (top_k)
        result = reranker.rerank("test", facts, top_k=5)
        
        assert len(result) == 5
        assert result == facts[:5]  # Original order


class TestGetReranker:
    """Test suite for get_reranker singleton function"""
    
    def test_get_reranker_returns_instance(self):
        """Test that get_reranker returns a CrossEncoderReranker instance"""
        reranker = get_reranker()
        assert isinstance(reranker, CrossEncoderReranker)
    
    def test_get_reranker_singleton_pattern(self):
        """Test that get_reranker returns the same instance (singleton)"""
        reranker1 = get_reranker()
        reranker2 = get_reranker()
        
        # Should be the exact same object
        assert reranker1 is reranker2
    
    def test_get_reranker_model_loaded_once(self):
        """Test that the model is loaded only once across multiple calls"""
        # Clear singleton
        import app.core.reranker
        app.core.reranker._reranker_instance = None
        
        # First call loads the model
        reranker1 = get_reranker()
        model1_id = id(reranker1.model)
        
        # Second call reuses the same model
        reranker2 = get_reranker()
        model2_id = id(reranker2.model)
        
        assert model1_id == model2_id


class TestIntegration:
    """Integration tests for reranking workflow"""
    
    def test_end_to_end_reranking(self):
        """Test complete reranking workflow"""
        reranker = get_reranker()
        
        # Realistic diving-related facts
        facts = [
            {"fact": "The maximum depth for recreational diving is 40 meters"},
            {"fact": "Always dive with a buddy for safety"},
            {"fact": "Check your equipment before every dive"},
            {"fact": "Decompression sickness can occur if you ascend too quickly"},
            {"fact": "The buddy system is a critical safety procedure"},
            {"fact": "Marine life should be observed but not touched"},
            {"fact": "Emergency procedures include controlled emergency swimming ascent"},
            {"fact": "Dive planning includes checking weather and currents"},
            {"fact": "Safety stops are recommended at 5 meters for 3 minutes"},
            {"fact": "Equipment maintenance extends the life of your gear"}
        ]
        
        query = "What are the safety procedures for recreational diving?"
        
        result = reranker.rerank(query, facts, top_k=5)
        
        # Assertions
        assert len(result) == 5
        
        # Safety-related facts should be prominent
        result_texts = [f["fact"].lower() for f in result]
        safety_count = sum(1 for text in result_texts if "safety" in text or "emergency" in text)
        
        # At least 2 safety-related facts in top 5
        assert safety_count >= 2
        
        # Should include buddy system (highly relevant to safety procedures)
        assert any("buddy" in text for text in result_texts)
    
    def test_reranking_improves_relevance(self):
        """Test that reranking improves relevance vs random order"""
        reranker = get_reranker()
        
        # Facts where relevant ones are NOT at the top
        facts = [
            {"fact": "Marine biology is fascinating", "id": 1},
            {"fact": "Underwater photography tips", "id": 2},
            {"fact": "Emergency ascent procedures are critical for safety", "id": 3},
            {"fact": "Dive computer maintenance", "id": 4},
            {"fact": "Safety checks before diving prevent accidents", "id": 5}
        ]
        
        query = "What are diving safety procedures?"
        
        result = reranker.rerank(query, facts, top_k=3)
        
        # The two safety-related facts (ids 3, 5) should be in top 3
        result_ids = [f["id"] for f in result]
        assert 3 in result_ids  # Emergency ascent (highly relevant)
        assert 5 in result_ids  # Safety checks (highly relevant)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

