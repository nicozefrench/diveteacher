#!/usr/bin/env python3
"""
Retrieval-Only A/B Test for Cross-Encoder Reranking

This script tests ONLY the retrieval + reranking performance,
WITHOUT LLM answer generation (which is slow on CPU Ollama).

Focus: Pure reranking quality and performance

Usage:
    python3 scripts/test_reranking_retrieval_only.py

Expected time: ~2-5 minutes (20 queries × 2 modes × 2-5s)
    
Author: DiveTeacher Team
Date: November 4, 2025
"""

import json
import asyncio
import httpx
import time
from typing import List, Dict, Any
from pathlib import Path
import statistics

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_QUERIES_FILE = "TestPDF/niveau1_test_queries.json"
RESULTS_FILE = "Devplan/251104-RERANKING-AB-TEST-RESULTS.md"
RAG_TOP_K = 5


def load_test_queries() -> List[Dict[str, Any]]:
    """Load test queries from JSON file"""
    with open(TEST_QUERIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all queries from all categories
    all_queries = []
    for category_name, category_data in data['categories'].items():
        for query in category_data['requetes']:
            query['category'] = category_name
            all_queries.append(query)
    
    return all_queries


async def run_retrieval_test(
    question: str, 
    use_reranking: bool, 
    client: httpx.AsyncClient
) -> Dict[str, Any]:
    """
    Test retrieval ONLY (no LLM generation)
    
    Calls internal retrieve_context() via custom test endpoint
    
    Returns:
        {
            'facts': List[Dict],
            'num_facts': int,
            'reranked': bool,
            'duration_ms': float
        }
    """
    start_time = time.time()
    
    try:
        # Call backend test endpoint that returns ONLY retrieval results
        response = await client.post(
            f"{API_BASE_URL}/api/test/retrieval",
            json={
                "question": question,
                "use_reranking": use_reranking,
                "top_k": RAG_TOP_K
            },
            timeout=30.0,
            follow_redirects=True
        )
        response.raise_for_status()
        result = response.json()
        
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            'facts': result['facts'],
            'num_facts': result['total'],
            'reranked': result.get('reranked', False),
            'duration_ms': duration_ms
        }
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return {
            'facts': [],
            'num_facts': 0,
            'reranked': False,
            'duration_ms': 0,
            'error': str(e)
        }


def score_relevance(
    facts: List[Dict[str, Any]], 
    relevant_keywords: List[str],
    irrelevant_keywords: List[str]
) -> Dict[str, Any]:
    """
    Score retrieval relevance based on keywords
    
    Scoring:
        - +1 for each relevant keyword found
        - -0.5 for each irrelevant keyword found
        - Precision = relevant_score / total possible relevant
    
    Returns:
        {
            'relevant_score': int,
            'irrelevant_score': int,
            'total_score': float,
            'precision': float (0-1),
            'relevant_keywords_found': List[str],
            'irrelevant_keywords_found': List[str]
        }
    """
    # Concatenate all facts text
    facts_text = " ".join([fact.get('fact', '').lower() for fact in facts])
    
    # Count relevant keywords
    relevant_found = []
    for keyword in relevant_keywords:
        if keyword.lower() in facts_text:
            relevant_found.append(keyword)
    
    # Count irrelevant keywords
    irrelevant_found = []
    for keyword in irrelevant_keywords:
        if keyword.lower() in facts_text:
            irrelevant_found.append(keyword)
    
    relevant_score = len(relevant_found)
    irrelevant_score = len(irrelevant_found)
    total_score = relevant_score - (irrelevant_score * 0.5)
    
    # Precision = relevant found / total relevant possible
    precision = relevant_score / len(relevant_keywords) if relevant_keywords else 0.0
    
    return {
        'relevant_score': relevant_score,
        'irrelevant_score': irrelevant_score,
        'total_score': total_score,
        'precision': precision,
        'relevant_keywords_found': relevant_found,
        'irrelevant_keywords_found': irrelevant_found
    }


async def run_ab_test():
    """Run A/B test comparing reranking ON vs OFF (retrieval only)"""
    
    print("=" * 80)
    print("🧪 A/B TEST: Cross-Encoder Reranking (RETRIEVAL ONLY - No LLM)")
    print("=" * 80)
    print()
    
    # Load test queries
    queries = load_test_queries()
    print(f"📋 Loaded {len(queries)} test queries")
    print()
    
    # Results storage
    results = []
    
    async with httpx.AsyncClient() as client:
        for idx, query_data in enumerate(queries, 1):
            query_id = query_data['id']
            question = query_data['question']
            category = query_data['category']
            relevant_kw = query_data['mots_cles_pertinents']
            irrelevant_kw = query_data['mots_cles_non_pertinents']
            
            print(f"[{idx}/{len(queries)}] Testing: {query_id} ({category})")
            print(f"   Question: {question[:60]}...")
            
            # Test WITHOUT reranking (baseline)
            print(f"   🔹 Baseline (no reranking)...", end=" ", flush=True)
            baseline_result = await run_retrieval_test(question, use_reranking=False, client=client)
            baseline_score = score_relevance(
                baseline_result['facts'], 
                relevant_kw, 
                irrelevant_kw
            )
            print(f"✅ {baseline_result['duration_ms']:.0f}ms | Precision: {baseline_score['precision']:.2%}")
            
            # Test WITH reranking (enhanced)
            print(f"   🔸 Enhanced (reranking)...", end=" ", flush=True)
            enhanced_result = await run_retrieval_test(question, use_reranking=True, client=client)
            enhanced_score = score_relevance(
                enhanced_result['facts'], 
                relevant_kw, 
                irrelevant_kw
            )
            print(f"✅ {enhanced_result['duration_ms']:.0f}ms | Precision: {enhanced_score['precision']:.2%}")
            
            # Calculate improvement
            precision_improvement = enhanced_score['precision'] - baseline_score['precision']
            improvement_pct = (precision_improvement / baseline_score['precision'] * 100) if baseline_score['precision'] > 0 else 0
            
            if precision_improvement > 0:
                print(f"   ✨ Improvement: +{improvement_pct:.1f}% (better)")
            elif precision_improvement < 0:
                print(f"   ⚠️  Degradation: {improvement_pct:.1f}% (worse)")
            else:
                print(f"   ➖ No change")
            
            print()
            
            # Store results
            results.append({
                'query_id': query_id,
                'category': category,
                'question': question,
                'relevant_keywords': relevant_kw,
                'irrelevant_keywords': irrelevant_kw,
                'baseline': {
                    'facts': baseline_result['facts'],
                    'num_facts': baseline_result['num_facts'],
                    'duration_ms': baseline_result['duration_ms'],
                    'score': baseline_score
                },
                'enhanced': {
                    'facts': enhanced_result['facts'],
                    'num_facts': enhanced_result['num_facts'],
                    'reranked': enhanced_result['reranked'],
                    'duration_ms': enhanced_result['duration_ms'],
                    'score': enhanced_score
                },
                'improvement': {
                    'precision_delta': precision_improvement,
                    'precision_pct': improvement_pct
                }
            })
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.2)
    
    return results


def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze A/B test results"""
    
    # Extract metrics
    baseline_precisions = [r['baseline']['score']['precision'] for r in results]
    enhanced_precisions = [r['enhanced']['score']['precision'] for r in results]
    precision_improvements = [r['improvement']['precision_delta'] for r in results]
    
    baseline_durations = [r['baseline']['duration_ms'] for r in results]
    enhanced_durations = [r['enhanced']['duration_ms'] for r in results]
    
    # Calculate statistics
    avg_baseline_precision = statistics.mean(baseline_precisions)
    avg_enhanced_precision = statistics.mean(enhanced_precisions)
    avg_precision_improvement = statistics.mean(precision_improvements)
    median_precision_improvement = statistics.median(precision_improvements)
    
    avg_baseline_duration = statistics.mean(baseline_durations)
    avg_enhanced_duration = statistics.mean(enhanced_durations)
    
    # Count improvements/degradations
    improvements = sum(1 for imp in precision_improvements if imp > 0)
    degradations = sum(1 for imp in precision_improvements if imp < 0)
    no_change = sum(1 for imp in precision_improvements if imp == 0)
    
    return {
        'total_queries': len(results),
        'baseline': {
            'avg_precision': avg_baseline_precision,
            'avg_duration_ms': avg_baseline_duration
        },
        'enhanced': {
            'avg_precision': avg_enhanced_precision,
            'avg_duration_ms': avg_enhanced_duration
        },
        'improvement': {
            'avg_precision_delta': avg_precision_improvement,
            'median_precision_delta': median_precision_improvement,
            'avg_precision_pct': (avg_precision_improvement / avg_baseline_precision * 100) if avg_baseline_precision > 0 else 0,
            'queries_improved': improvements,
            'queries_degraded': degradations,
            'queries_no_change': no_change,
            'improvement_rate': (improvements / len(results) * 100) if results else 0
        },
        'performance': {
            'avg_duration_increase_ms': avg_enhanced_duration - avg_baseline_duration,
            'avg_duration_increase_pct': ((avg_enhanced_duration - avg_baseline_duration) / avg_baseline_duration * 100) if avg_baseline_duration > 0 else 0
        }
    }


def generate_markdown_report(results: List[Dict[str, Any]], analysis: Dict[str, Any]):
    """Generate detailed markdown report"""
    
    report = f"""# A/B Test Results: Cross-Encoder Reranking (Retrieval Only)

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Test Type:** RETRIEVAL ONLY (no LLM generation)  
**Test Dataset:** Niveau 1 (PE20) - {analysis['total_queries']} queries  
**Model:** ms-marco-MiniLM-L-6-v2  
**Configuration:** RAG_TOP_K={RAG_TOP_K}, RETRIEVAL_MULTIPLIER=4

---

## 📊 EXECUTIVE SUMMARY

### Quality Improvement (Retrieval Precision)
- **Average Baseline Precision:** {analysis['baseline']['avg_precision']:.2%}
- **Average Enhanced Precision:** {analysis['enhanced']['avg_precision']:.2%}
- **Average Improvement:** **+{analysis['improvement']['avg_precision_pct']:.1f}%** ({analysis['improvement']['avg_precision_delta']:+.4f})
- **Median Improvement:** {analysis['improvement']['median_precision_delta']:+.4f}

### Query-Level Results
- **Queries Improved:** {analysis['improvement']['queries_improved']}/{analysis['total_queries']} ({analysis['improvement']['improvement_rate']:.1f}%)
- **Queries Degraded:** {analysis['improvement']['queries_degraded']}/{analysis['total_queries']}
- **Queries Unchanged:** {analysis['improvement']['queries_no_change']}/{analysis['total_queries']}

### Performance Impact (Retrieval Only)
- **Baseline Duration:** {analysis['baseline']['avg_duration_ms']:.0f}ms
- **Enhanced Duration:** {analysis['enhanced']['avg_duration_ms']:.0f}ms
- **Duration Increase:** +{analysis['performance']['avg_duration_increase_ms']:.0f}ms ({analysis['performance']['avg_duration_increase_pct']:+.1f}%)

---

## 🎯 VERDICT

"""
    
    # Verdict based on results
    if analysis['improvement']['avg_precision_pct'] >= 10:
        report += f"""✅ **SUCCESS: Reranking significantly improves retrieval quality (+{analysis['improvement']['avg_precision_pct']:.1f}%)**

The cross-encoder reranking meets the expected improvement target (≥10%) with acceptable performance overhead.

**Recommendation:** ✅ Deploy to production (keep RAG_RERANKING_ENABLED=True)
"""
    elif analysis['improvement']['avg_precision_pct'] >= 5:
        report += f"""⚠️ **PARTIAL SUCCESS: Moderate improvement (+{analysis['improvement']['avg_precision_pct']:.1f}%)**

The reranking shows improvement but below the target (10-15%).

**Recommendation:** ⚠️ Review configuration (consider increasing RETRIEVAL_MULTIPLIER)
"""
    else:
        report += f"""❌ **BELOW EXPECTATIONS: Minimal improvement (+{analysis['improvement']['avg_precision_pct']:.1f}%)**

The reranking does not meet the expected improvement target.

**Recommendation:** ❌ Investigate issues before production deployment
"""
    
    report += f"""
---

## 📋 DETAILED RESULTS BY CATEGORY

"""
    
    # Group by category
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    # Report per category
    for cat_name, cat_results in categories.items():
        report += f"""
### {cat_name.upper()} ({len(cat_results)} queries)

"""
        for r in cat_results:
            baseline_prec = r['baseline']['score']['precision']
            enhanced_prec = r['enhanced']['score']['precision']
            improvement_pct = r['improvement']['precision_pct']
            
            status = "✅" if improvement_pct > 0 else ("⚠️" if improvement_pct < 0 else "➖")
            
            report += f"""**{r['query_id']}:** {r['question'][:80]}...
- Baseline: {baseline_prec:.2%} | Enhanced: {enhanced_prec:.2%} | {status} {improvement_pct:+.1f}%

"""
    
    report += f"""
---

## 📈 PERFORMANCE ANALYSIS (Retrieval Only - No LLM)

### Retrieval Duration Comparison

| Metric | Baseline (No Reranking) | Enhanced (With Reranking) | Delta |
|--------|-------------------------|---------------------------|-------|
| Average | {analysis['baseline']['avg_duration_ms']:.0f}ms | {analysis['enhanced']['avg_duration_ms']:.0f}ms | +{analysis['performance']['avg_duration_increase_ms']:.0f}ms |
| Percentage | 100% | {100 + analysis['performance']['avg_duration_increase_pct']:.1f}% | +{analysis['performance']['avg_duration_increase_pct']:.1f}% |

**Verdict:** Performance overhead is {"✅ acceptable (<200ms)" if analysis['performance']['avg_duration_increase_ms'] < 200 else "⚠️ above target (>200ms)"}

---

## 💡 CONCLUSIONS

### Key Findings

1. **Quality Improvement:** {analysis['improvement']['queries_improved']}/{analysis['total_queries']} queries improved ({analysis['improvement']['improvement_rate']:.1f}%)
2. **Average Gain:** +{analysis['improvement']['avg_precision_pct']:.1f}% retrieval precision
3. **Performance Cost:** +{analysis['performance']['avg_duration_increase_ms']:.0f}ms per query (+{analysis['performance']['avg_duration_increase_pct']:.1f}%)

### Test Method

**IMPORTANT:** This test evaluates **RETRIEVAL QUALITY ONLY** (Graphiti search + reranking).

- ✅ **What we tested:** Cross-encoder reranking effectiveness
- ❌ **What we skipped:** LLM answer generation (too slow on CPU Ollama)
- ⚡ **Test duration:** ~2-5 minutes (vs ~80 minutes with full RAG pipeline)

### Recommendations

"""
    
    if analysis['improvement']['avg_precision_pct'] >= 10:
        report += """✅ **Deploy to Production**
- Enable reranking by default (RAG_RERANKING_ENABLED=True)
- Monitor retrieval quality in production
- Collect user feedback on answer quality

"""
    else:
        report += """⚠️ **Further Investigation Needed**
- Review retrieval configuration (RETRIEVAL_MULTIPLIER)
- Analyze queries with degraded performance
- Consider alternative reranker models

"""
    
    report += f"""---

**Test Status:** ✅ COMPLETED  
**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Script:** scripts/test_reranking_retrieval_only.py
"""
    
    # Save report
    Path(RESULTS_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📝 Report saved to: {RESULTS_FILE}")


async def main():
    """Main entry point"""
    try:
        # Run A/B test
        results = await run_ab_test()
        
        # Analyze results
        print("=" * 80)
        print("📊 ANALYZING RESULTS")
        print("=" * 80)
        print()
        
        analysis = analyze_results(results)
        
        # Print summary
        print(f"✅ A/B Test Complete (Retrieval Only)")
        print(f"   • Total Queries: {analysis['total_queries']}")
        print(f"   • Average Improvement: +{analysis['improvement']['avg_precision_pct']:.1f}%")
        print(f"   • Queries Improved: {analysis['improvement']['queries_improved']}/{analysis['total_queries']}")
        print(f"   • Performance Impact: +{analysis['performance']['avg_duration_increase_ms']:.0f}ms")
        print()
        
        # Generate report
        generate_markdown_report(results, analysis)
        
        print("=" * 80)
        print("✅ A/B TEST COMPLETE (RETRIEVAL ONLY - NO LLM)")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))

