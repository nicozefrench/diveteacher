#!/usr/bin/env python3
"""
GAP #3 DAY 2.4: Run A/B Test (Adapted for Docling-only validation)

According to plan (line 427-475):
- Load 20 test queries from niveau1_test_queries.json
- Test against enhanced database (Docling HybridChunker)
- Calculate precision based on relevant keywords
- Generate detailed results report

Note: Since ARIA baseline was skipped (already replaced), this validates
that Docling HybridChunker provides good retrieval quality.
"""
import sys
import json
import requests
import time
from datetime import datetime
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
QUERIES_PATH = "/Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter/backend/tests/data/niveau1_test_queries.json"
RESULTS_PATH = "/Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter/scripts/gap3_day2.4_ab_test_results.json"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def load_test_queries():
    """Load 20 test queries from JSON"""
    print_section("LOADING TEST QUERIES")
    
    with open(QUERIES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all queries from all categories
    queries = []
    for category_name, category_data in data['categories'].items():
        for query in category_data['requetes']:
            query['category'] = category_name
            queries.append(query)
    
    print(f"✅ Loaded {len(queries)} queries from dataset")
    print(f"📊 Categories:")
    for cat in data['categories']:
        count = data['categories'][cat]['nombre']
        print(f"   - {cat}: {count} queries")
    
    return queries

def execute_query(question: str, query_id: str) -> dict:
    """Execute a single query against the backend"""
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/api/query/",  # Trailing slash required to avoid 307 redirect
            json={"question": question},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "elapsed_time": elapsed
            }
        
        result = response.json()
        
        # FIXED: API returns 'facts' not 'sources' (Graphiti structure)
        context = result.get('context', {})
        facts = context.get('facts', [])
        
        return {
            "success": True,
            "answer": result.get('answer', ''),
            "context": context,
            "facts": facts,
            "sources": facts,  # Alias for backward compatibility with precision calculation
            "num_sources": result.get('num_sources', len(facts)),
            "elapsed_time": elapsed
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": 0
        }

def calculate_precision(answer: str, facts: list, relevant_keywords: list, irrelevant_keywords: list) -> dict:
    """
    Calculate precision score based on keyword presence
    
    Scoring:
    - +1 point for each relevant keyword found
    - -0.5 points for each irrelevant keyword found
    - Normalize to 0-100%
    """
    answer_lower = answer.lower()
    
    # FIXED: Extract text from Graphiti facts (not 'text' field but 'fact' field)
    facts_text = " ".join([f.get('fact', '') if isinstance(f, dict) else str(f) for f in facts]).lower()
    combined_text = (answer_lower + " " + facts_text).lower()
    
    relevant_found = []
    irrelevant_found = []
    
    # Check relevant keywords
    for keyword in relevant_keywords:
        if keyword.lower() in combined_text:
            relevant_found.append(keyword)
    
    # Check irrelevant keywords
    for keyword in irrelevant_keywords:
        if keyword.lower() in combined_text:
            irrelevant_found.append(keyword)
    
    # Calculate score
    relevant_score = len(relevant_found)
    irrelevant_penalty = len(irrelevant_found) * 0.5
    raw_score = max(0, relevant_score - irrelevant_penalty)
    
    # Normalize to percentage
    max_score = len(relevant_keywords)
    precision_pct = (raw_score / max_score * 100) if max_score > 0 else 0
    
    return {
        "precision_pct": precision_pct,
        "relevant_found": relevant_found,
        "relevant_total": len(relevant_keywords),
        "irrelevant_found": irrelevant_found,
        "raw_score": raw_score,
        "max_score": max_score
    }

def run_ab_test(queries: list):
    """Run A/B test on all queries"""
    print_section("RUNNING A/B TEST")
    print(f"Testing {len(queries)} queries against Docling HybridChunker database")
    print(f"Expected improvement: +7-10% over baseline (if we had one)")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        query_id = query['id']
        question = query['question']
        category = query['category']
        relevant_keywords = query['mots_cles_pertinents']
        irrelevant_keywords = query['mots_cles_non_pertinents']
        
        print(f"\n[{i}/{len(queries)}] {query_id} ({category})")
        print(f"   Q: {question[:70]}...")
        
        # Execute query
        result = execute_query(question, query_id)
        
        if not result['success']:
            print(f"   ❌ FAILED: {result['error']}")
            results.append({
                "query_id": query_id,
                "category": category,
                "question": question,
                "success": False,
                "error": result['error'],
                "elapsed_time": result['elapsed_time']
            })
            continue
        
        # Calculate precision
        precision = calculate_precision(
            result['answer'],
            result['facts'],
            relevant_keywords,
            irrelevant_keywords
        )
        
        print(f"   ✅ Precision: {precision['precision_pct']:.1f}% "
              f"({precision['relevant_found']}/{precision['relevant_total']} keywords)")
        print(f"   📚 Facts retrieved: {result['num_sources']}")
        print(f"   ⏱️  Response time: {result['elapsed_time']:.2f}s")
        
        # Store result
        results.append({
            "query_id": query_id,
            "category": category,
            "question": question,
            "success": True,
            "answer": result['answer'][:200],  # Truncate for storage
            "sources_count": result['num_sources'],
            "facts_count": len(result['facts']),
            "elapsed_time": result['elapsed_time'],
            "precision": precision
        })
    
    return results

def analyze_results(results: list):
    """Analyze A/B test results"""
    print_section("ANALYZING RESULTS")
    
    successful_results = [r for r in results if r['success']]
    failed_results = [r for r in results if not r['success']]
    
    print(f"📊 Test Execution:")
    print(f"   Total queries: {len(results)}")
    print(f"   Successful: {len(successful_results)}")
    print(f"   Failed: {len(failed_results)}")
    
    if not successful_results:
        print(f"\n❌ No successful queries! Cannot calculate metrics.")
        return {}
    
    # Calculate precision stats
    precisions = [r['precision']['precision_pct'] for r in successful_results]
    avg_precision = sum(precisions) / len(precisions)
    min_precision = min(precisions)
    max_precision = max(precisions)
    
    # Calculate response time stats
    response_times = [r['elapsed_time'] for r in successful_results]
    avg_response_time = sum(response_times) / len(response_times)
    
    # Category breakdown
    categories = {}
    for r in successful_results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r['precision']['precision_pct'])
    
    print(f"\n📈 Precision Metrics:")
    print(f"   Average: {avg_precision:.1f}%")
    print(f"   Min: {min_precision:.1f}%")
    print(f"   Max: {max_precision:.1f}%")
    
    print(f"\n⏱️  Response Time:")
    print(f"   Average: {avg_response_time:.2f}s")
    
    print(f"\n📂 Category Breakdown:")
    for cat, prec_list in categories.items():
        cat_avg = sum(prec_list) / len(prec_list)
        print(f"   {cat}: {cat_avg:.1f}% ({len(prec_list)} queries)")
    
    # Identify best and worst queries
    sorted_results = sorted(successful_results, key=lambda x: x['precision']['precision_pct'], reverse=True)
    
    print(f"\n🏆 Top 3 Queries:")
    for i, r in enumerate(sorted_results[:3], 1):
        print(f"   {i}. {r['query_id']}: {r['precision']['precision_pct']:.1f}%")
        print(f"      Q: {r['question'][:60]}...")
    
    print(f"\n⚠️  Bottom 3 Queries:")
    for i, r in enumerate(sorted_results[-3:], 1):
        print(f"   {i}. {r['query_id']}: {r['precision']['precision_pct']:.1f}%")
        print(f"      Q: {r['question'][:60]}...")
    
    return {
        "total_queries": len(results),
        "successful_queries": len(successful_results),
        "failed_queries": len(failed_results),
        "avg_precision": avg_precision,
        "min_precision": min_precision,
        "max_precision": max_precision,
        "avg_response_time": avg_response_time,
        "category_breakdown": {cat: sum(prec_list)/len(prec_list) for cat, prec_list in categories.items()}
    }

def generate_report(results: list, analysis: dict):
    """Generate JSON report"""
    print_section("GENERATING REPORT")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "day": "2.4",
        "task": "A/B Test - Docling HybridChunker Validation",
        "database": "Enhanced (Docling HybridChunker with contextualization)",
        "note": "ARIA baseline skipped (already replaced by Docling)",
        "results": results,
        "analysis": analysis,
        "validation": {
            "target_precision": "80-90%",
            "actual_precision": f"{analysis.get('avg_precision', 0):.1f}%",
            "status": "PASS" if analysis.get('avg_precision', 0) >= 80 else "NEEDS_IMPROVEMENT"
        }
    }
    
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Report saved to: {RESULTS_PATH}")
    print(f"\n📋 Report Summary:")
    print(json.dumps(report['analysis'], indent=2))
    print(f"\n✅ Validation Status: {report['validation']['status']}")
    print(f"   Target: {report['validation']['target_precision']}")
    print(f"   Actual: {report['validation']['actual_precision']}")
    
    return report

def main():
    print_section("GAP #3 DAY 2.4: A/B TEST - DOCLING VALIDATION")
    print("Task: Test 20 queries against Docling HybridChunker database")
    print("Expected: 80-90% average precision")
    print("Note: ARIA baseline skipped (already replaced by Docling)")
    
    # Load queries
    queries = load_test_queries()
    
    # Run A/B test
    results = run_ab_test(queries)
    
    # Analyze results
    analysis = analyze_results(results)
    
    if not analysis:
        print("\n❌ DAY 2.4 FAILED: No successful queries")
        sys.exit(1)
    
    # Generate report
    report = generate_report(results, analysis)
    
    # Final summary
    print_section("✅ DAY 2.4 COMPLETE!")
    print(f"A/B Test executed successfully")
    print(f"✅ {analysis['successful_queries']}/{analysis['total_queries']} queries successful")
    print(f"✅ Average precision: {analysis['avg_precision']:.1f}%")
    print(f"✅ Average response time: {analysis['avg_response_time']:.2f}s")
    print(f"\n🎯 NEXT: DAY 2.5 - Analyze Results and validate +7-10% improvement")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

