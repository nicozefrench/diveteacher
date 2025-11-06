#!/usr/bin/env python3
"""
Performance Benchmarking Script for Cross-Encoder Reranking

Measures the performance overhead of reranking to ensure it stays
within acceptable limits (<500ms total retrieval time).

Usage:
    python scripts/benchmark_reranking.py

Requirements:
    - Backend running on http://localhost:8000
    - Neo4j populated with test data
"""

import json
import time
import httpx
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import statistics

# Configuration
API_BASE_URL = "http://localhost:8000/api/query/"
BENCHMARK_ITERATIONS = 10  # Number of iterations per configuration
TEST_QUERY = "Quelle est la profondeur maximale autorisée pour un plongeur niveau 1 ?"
TIMEOUT = 30.0

def benchmark_query(use_reranking: bool, iterations: int = BENCHMARK_ITERATIONS) -> Dict[str, Any]:
    """
    Benchmark a query configuration multiple times.
    
    Args:
        use_reranking: Enable reranking
        iterations: Number of iterations to run
        
    Returns:
        Statistics dict with min, max, avg, median times
    """
    durations = []
    errors = 0
    
    payload = {
        "question": TEST_QUERY,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 100,
        "use_reranking": use_reranking
    }
    
    print(f"\n{'─'*80}")
    print(f"Configuration: {'WITH reranking' if use_reranking else 'WITHOUT reranking'}")
    print(f"Iterations: {iterations}")
    print(f"{'─'*80}\n")
    
    for i in range(iterations):
        start_time = time.time()
        
        try:
            with httpx.Client(timeout=TIMEOUT) as client:
                response = client.post(API_BASE_URL, json=payload)
                response.raise_for_status()
                
                duration = time.time() - start_time
                durations.append(duration)
                
                result = response.json()
                num_facts = len(result.get("context", {}).get("facts", []))
                reranked = result.get("reranked", False)
                
                print(f"  Iteration {i+1}/{iterations}: {duration*1000:.0f}ms "
                      f"({num_facts} facts{', reranked' if reranked else ''})")
                
        except Exception as e:
            errors += 1
            print(f"  Iteration {i+1}/{iterations}: ❌ Error: {e}")
        
        time.sleep(0.5)  # Brief pause between iterations
    
    if not durations:
        return {
            "error": "All iterations failed",
            "errors": errors,
            "iterations": iterations
        }
    
    stats = {
        "iterations": iterations,
        "errors": errors,
        "success_rate": ((iterations - errors) / iterations) * 100,
        "durations_ms": {
            "min": min(durations) * 1000,
            "max": max(durations) * 1000,
            "avg": statistics.mean(durations) * 1000,
            "median": statistics.median(durations) * 1000,
            "stdev": statistics.stdev(durations) * 1000 if len(durations) > 1 else 0
        }
    }
    
    print(f"\n📊 Statistics:")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Min: {stats['durations_ms']['min']:.0f}ms")
    print(f"  Max: {stats['durations_ms']['max']:.0f}ms")
    print(f"  Avg: {stats['durations_ms']['avg']:.0f}ms")
    print(f"  Median: {stats['durations_ms']['median']:.0f}ms")
    print(f"  StdDev: {stats['durations_ms']['stdev']:.0f}ms")
    
    return stats

def run_benchmark():
    """Run performance benchmark."""
    
    print("\n" + "="*80)
    print("⚡ PERFORMANCE BENCHMARK: Cross-Encoder Reranking")
    print("="*80 + "\n")
    
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API endpoint: {API_BASE_URL}")
    print(f"🔍 Test query: {TEST_QUERY}")
    print(f"🔁 Iterations: {BENCHMARK_ITERATIONS} per configuration")
    
    # Benchmark WITHOUT reranking (baseline)
    baseline_stats = benchmark_query(use_reranking=False, iterations=BENCHMARK_ITERATIONS)
    
    time.sleep(2)  # Pause between configurations
    
    # Benchmark WITH reranking (enhanced)
    enhanced_stats = benchmark_query(use_reranking=True, iterations=BENCHMARK_ITERATIONS)
    
    # Summary comparison
    print("\n" + "="*80)
    print("📊 PERFORMANCE COMPARISON")
    print("="*80 + "\n")
    
    if "error" not in baseline_stats and "error" not in enhanced_stats:
        baseline_avg = baseline_stats["durations_ms"]["avg"]
        enhanced_avg = enhanced_stats["durations_ms"]["avg"]
        overhead = enhanced_avg - baseline_avg
        overhead_pct = (overhead / baseline_avg) * 100
        
        print(f"Baseline (WITHOUT reranking):")
        print(f"  Average: {baseline_avg:.0f}ms")
        print(f"  Median: {baseline_stats['durations_ms']['median']:.0f}ms")
        
        print(f"\nEnhanced (WITH reranking):")
        print(f"  Average: {enhanced_avg:.0f}ms")
        print(f"  Median: {enhanced_stats['durations_ms']['median']:.0f}ms")
        
        print(f"\nOverhead:")
        print(f"  Absolute: {overhead:+.0f}ms")
        print(f"  Relative: {overhead_pct:+.1f}%")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if enhanced_avg < 500:
            print(f"  ✅ PASS: Total retrieval time ({enhanced_avg:.0f}ms) < 500ms target")
        else:
            print(f"  ⚠️  WARNING: Total retrieval time ({enhanced_avg:.0f}ms) > 500ms target")
        
        if overhead < 200:
            print(f"  ✅ PASS: Reranking overhead ({overhead:.0f}ms) < 200ms target")
        else:
            print(f"  ⚠️  WARNING: Reranking overhead ({overhead:.0f}ms) > 200ms target")
    
    # Save results
    output_file = Path("scripts/benchmark_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "test_query": TEST_QUERY,
            "iterations": BENCHMARK_ITERATIONS,
            "baseline": baseline_stats,
            "enhanced": enhanced_stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"\n⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)

if __name__ == "__main__":
    run_benchmark()
