#!/usr/bin/env python3
"""
A/B Testing Script for Cross-Encoder Reranking

Compares RAG query results with and without reranking to measure
the impact on retrieval precision.

Usage:
    python scripts/test_reranking_ab.py

Requirements:
    - Backend running on http://localhost:8000
    - Neo4j populated with Niveau 1.pdf data
    - Test queries in TestPDF/niveau1_test_queries.json
"""

import json
import time
import httpx
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api/query/"
QUERIES_FILE = Path("TestPDF/niveau1_test_queries.json")
TIMEOUT = 30.0  # seconds per query

def load_test_queries() -> List[Dict[str, Any]]:
    """Load test queries from JSON file."""
    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = []
    for category, cat_data in data.get("categories", {}).items():
        for query in cat_data.get("requetes", []):
            queries.append({
                "id": query["id"],
                "category": category,
                "question": query["question"],
                "expected_answer": query["reponse_attendue"],
                "relevant_keywords": query["mots_cles_pertinents"],
                "irrelevant_keywords": query["mots_cles_non_pertinents"],
                "page_source": query["page_source"]
            })
    
    return queries

def run_query(question: str, use_reranking: bool) -> Dict[str, Any]:
    """
    Run a single RAG query with or without reranking.
    
    Args:
        question: User's question
        use_reranking: Enable reranking
        
    Returns:
        API response dict with facts, answer, timing
    """
    payload = {
        "question": question,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 200,
        "use_reranking": use_reranking
    }
    
    start_time = time.time()
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(API_BASE_URL, json=payload)
            response.raise_for_status()
            
            duration = time.time() - start_time
            result = response.json()
            result["query_duration"] = duration
            
            return result
            
    except httpx.TimeoutException:
        print(f"⏱️  Timeout after {TIMEOUT}s")
        return {"error": "timeout", "query_duration": TIMEOUT}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "query_duration": time.time() - start_time}

def calculate_precision(facts: List[Dict[str, Any]], relevant_keywords: List[str]) -> float:
    """
    Calculate precision: ratio of relevant facts retrieved.
    
    A fact is considered relevant if it contains at least one relevant keyword.
    """
    if not facts:
        return 0.0
    
    relevant_count = 0
    for fact in facts:
        fact_text = fact.get("fact", "").lower()
        for keyword in relevant_keywords:
            if keyword.lower() in fact_text:
                relevant_count += 1
                break  # Count each fact only once
    
    return (relevant_count / len(facts)) * 100.0

def run_ab_test():
    """Run A/B test comparing with and without reranking."""
    
    print("\n" + "="*80)
    print("📊 A/B TEST: Cross-Encoder Reranking Impact")
    print("="*80 + "\n")
    
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Test queries: {QUERIES_FILE}")
    print(f"🌐 API endpoint: {API_BASE_URL}")
    print(f"⏱️  Timeout: {TIMEOUT}s per query\n")
    
    # Load test queries
    queries = load_test_queries()
    print(f"✅ Loaded {len(queries)} test queries\n")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─'*80}")
        print(f"Query {i}/{len(queries)}: {query['id']} ({query['category']})")
        print(f"Question: {query['question']}")
        print(f"{'─'*80}\n")
        
        # Run WITHOUT reranking (baseline)
        print("🔵 Running WITHOUT reranking (baseline)...")
        baseline = run_query(query["question"], use_reranking=False)
        
        if "error" in baseline:
            print(f"   ❌ Error: {baseline['error']}")
            baseline_precision = 0.0
            baseline_num_facts = 0
        else:
            baseline_facts = baseline.get("context", {}).get("facts", [])
            baseline_num_facts = len(baseline_facts)
            baseline_precision = calculate_precision(
                baseline_facts,
                query["relevant_keywords"]
            )
            print(f"   ✅ Retrieved {baseline_num_facts} facts")
            print(f"   📊 Precision: {baseline_precision:.1f}%")
            print(f"   ⏱️  Duration: {baseline.get('query_duration', 0):.2f}s")
        
        time.sleep(1)  # Brief pause between queries
        
        # Run WITH reranking (enhanced)
        print("\n🟢 Running WITH reranking (enhanced)...")
        enhanced = run_query(query["question"], use_reranking=True)
        
        if "error" in enhanced:
            print(f"   ❌ Error: {enhanced['error']}")
            enhanced_precision = 0.0
            enhanced_num_facts = 0
        else:
            enhanced_facts = enhanced.get("context", {}).get("facts", [])
            enhanced_num_facts = len(enhanced_facts)
            enhanced_precision = calculate_precision(
                enhanced_facts,
                query["relevant_keywords"]
            )
            print(f"   ✅ Retrieved {enhanced_num_facts} facts")
            print(f"   📊 Precision: {enhanced_precision:.1f}%")
            print(f"   ⏱️  Duration: {enhanced.get('query_duration', 0):.2f}s")
            print(f"   🔁 Reranked: {enhanced.get('reranked', False)}")
        
        # Calculate improvement
        improvement = enhanced_precision - baseline_precision
        improvement_pct = (improvement / baseline_precision * 100) if baseline_precision > 0 else 0
        
        print(f"\n📈 Improvement: {improvement:+.1f}% absolute ({improvement_pct:+.1f}% relative)")
        
        results.append({
            "query_id": query["id"],
            "category": query["category"],
            "question": query["question"],
            "baseline": {
                "num_facts": baseline_num_facts,
                "precision": baseline_precision,
                "duration": baseline.get("query_duration", 0)
            },
            "enhanced": {
                "num_facts": enhanced_num_facts,
                "precision": enhanced_precision,
                "duration": enhanced.get("query_duration", 0),
                "reranked": enhanced.get("reranked", False)
            },
            "improvement": {
                "absolute": improvement,
                "relative": improvement_pct
            }
        })
    
    # Summary statistics
    print("\n" + "="*80)
    print("📊 SUMMARY STATISTICS")
    print("="*80 + "\n")
    
    avg_baseline_precision = sum(r["baseline"]["precision"] for r in results) / len(results)
    avg_enhanced_precision = sum(r["enhanced"]["precision"] for r in results) / len(results)
    avg_improvement = avg_enhanced_precision - avg_baseline_precision
    avg_improvement_pct = (avg_improvement / avg_baseline_precision * 100) if avg_baseline_precision > 0 else 0
    
    avg_baseline_duration = sum(r["baseline"]["duration"] for r in results) / len(results)
    avg_enhanced_duration = sum(r["enhanced"]["duration"] for r in results) / len(results)
    
    print(f"Total queries: {len(results)}")
    print(f"\nBaseline (WITHOUT reranking):")
    print(f"  Average precision: {avg_baseline_precision:.2f}%")
    print(f"  Average duration: {avg_baseline_duration:.2f}s")
    
    print(f"\nEnhanced (WITH reranking):")
    print(f"  Average precision: {avg_enhanced_precision:.2f}%")
    print(f"  Average duration: {avg_enhanced_duration:.2f}s")
    
    print(f"\nImprovement:")
    print(f"  Absolute: {avg_improvement:+.2f}%")
    print(f"  Relative: {avg_improvement_pct:+.2f}%")
    
    duration_overhead = avg_enhanced_duration - avg_baseline_duration
    print(f"  Duration overhead: {duration_overhead:+.2f}s ({duration_overhead/avg_baseline_duration*100:+.1f}%)")
    
    # Save results to JSON
    output_file = Path("scripts/ab_test_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_queries": len(results),
            "summary": {
                "baseline": {
                    "avg_precision": avg_baseline_precision,
                    "avg_duration": avg_baseline_duration
                },
                "enhanced": {
                    "avg_precision": avg_enhanced_precision,
                    "avg_duration": avg_enhanced_duration
                },
                "improvement": {
                    "absolute": avg_improvement,
                    "relative": avg_improvement_pct,
                    "duration_overhead": duration_overhead
                }
            },
            "detailed_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"\n⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)

if __name__ == "__main__":
    run_ab_test()
