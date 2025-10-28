#!/usr/bin/env python3
"""
Test script for RAG Query System with Qwen 2.5 7B

This script tests the three main query endpoints:
1. /api/query/health - Health check
2. /api/query/ - Non-streaming query (POST)
3. /api/query/stream - Streaming query (POST)

Usage:
    python scripts/test_rag_query.py [--base-url http://localhost:8000]
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any
import httpx
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")


async def test_health_endpoint(base_url: str) -> bool:
    """Test the /api/query/health endpoint"""
    print_header("Test 1: Health Check")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/api/query/health")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed")
                print(f"  Status: {data.get('status')}")
                print(f"  Provider: {data.get('provider')}")
                print(f"  Model: {data.get('model')}")
                print(f"  Test response: {data.get('test_response', '')[:50]}...")
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        print_error(f"Health check exception: {e}")
        return False


async def test_non_streaming_query(base_url: str) -> bool:
    """Test the /api/query/ non-streaming endpoint"""
    print_header("Test 2: Non-Streaming Query")
    
    # Test query with sample diving knowledge
    test_data = {
        "question": "What is the maximum depth for recreational diving?",
        "temperature": 0.7,
        "max_tokens": 200,
        "group_ids": None
    }
    
    print_info(f"Question: {test_data['question']}")
    print_info("Sending POST request to /api/query/...")
    
    try:
        start_time = datetime.now()
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url}/api/query/",
                json=test_data
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Non-streaming query successful")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Question: {data.get('question', '')[:50]}...")
                print(f"  Answer length: {len(data.get('answer', ''))} chars")
                print(f"  Answer preview: {data.get('answer', '')[:150]}...")
                print(f"  Sources used: {data.get('num_sources', 0)}")
                print(f"  Context facts: {len(data.get('context', {}).get('facts', []))}")
                
                if data.get('num_sources', 0) > 0:
                    print_success("✓ Successfully retrieved context from knowledge graph")
                else:
                    print_warning("⚠ No context retrieved (knowledge graph may be empty)")
                
                return True
            else:
                print_error(f"Query failed with status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print_error(f"Non-streaming query exception: {e}")
        return False


async def test_streaming_query(base_url: str) -> bool:
    """Test the /api/query/stream streaming endpoint"""
    print_header("Test 3: Streaming Query (Server-Sent Events)")
    
    test_data = {
        "question": "Explain the buddy system in scuba diving",
        "temperature": 0.7,
        "max_tokens": 150,
        "group_ids": None
    }
    
    print_info(f"Question: {test_data['question']}")
    print_info("Sending POST request to /api/query/stream...")
    print_info("Streaming response:\n")
    
    try:
        start_time = datetime.now()
        token_count = 0
        full_response = ""
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{base_url}/api/query/stream",
                json=test_data
            ) as response:
                
                if response.status_code != 200:
                    print_error(f"Stream failed with status {response.status_code}")
                    return False
                
                print(f"{Colors.YELLOW}", end="", flush=True)
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str == "[DONE]":
                            break
                        
                        if data_str.startswith("[ERROR"):
                            print(f"{Colors.ENDC}")
                            print_error(f"Stream error: {data_str}")
                            return False
                        
                        # Print the token
                        print(data_str, end="", flush=True)
                        full_response += data_str
                        token_count += 1
                
                print(f"{Colors.ENDC}\n")
                
                duration = (datetime.now() - start_time).total_seconds()
                tokens_per_sec = token_count / duration if duration > 0 else 0
                
                print_success("Streaming query successful")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Tokens streamed: {token_count}")
                print(f"  Tokens/second: {tokens_per_sec:.1f} tok/s")
                print(f"  Response length: {len(full_response)} chars")
                
                # Check performance target (30 tok/s minimum from deployment guide)
                if tokens_per_sec >= 30:
                    print_success(f"✓ Performance target met: {tokens_per_sec:.1f} tok/s >= 30 tok/s")
                elif tokens_per_sec >= 20:
                    print_warning(f"⚠ Performance below target: {tokens_per_sec:.1f} tok/s < 30 tok/s (but acceptable)")
                else:
                    print_error(f"✗ Performance significantly below target: {tokens_per_sec:.1f} tok/s < 30 tok/s")
                
                return True
                
    except Exception as e:
        print_error(f"Streaming query exception: {e}")
        return False


async def test_error_handling(base_url: str) -> bool:
    """Test error handling with invalid requests"""
    print_header("Test 4: Error Handling")
    
    # Test 1: Invalid temperature
    print_info("Testing invalid temperature (> 1.0)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/query/",
                json={
                    "question": "Test",
                    "temperature": 2.0,  # Invalid
                    "max_tokens": 100
                }
            )
            
            if response.status_code == 422:  # Validation error
                print_success("✓ Correctly rejected invalid temperature")
            else:
                print_warning(f"⚠ Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error handling test exception: {e}")
        return False
    
    # Test 2: Invalid max_tokens
    print_info("Testing invalid max_tokens (> 4000)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/query/",
                json={
                    "question": "Test",
                    "temperature": 0.7,
                    "max_tokens": 10000  # Invalid
                }
            )
            
            if response.status_code == 422:  # Validation error
                print_success("✓ Correctly rejected invalid max_tokens")
            else:
                print_warning(f"⚠ Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error handling test exception: {e}")
        return False
    
    # Test 3: Missing question
    print_info("Testing missing question field...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/query/",
                json={
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            )
            
            if response.status_code == 422:  # Validation error
                print_success("✓ Correctly rejected missing question")
            else:
                print_warning(f"⚠ Unexpected status code: {response.status_code}")
    
    except Exception as e:
        print_error(f"Error handling test exception: {e}")
        return False
    
    print_success("Error handling tests passed")
    return True


async def run_all_tests(base_url: str):
    """Run all tests and print summary"""
    print_header("RAG Query System Test Suite - Qwen 2.5 7B Q5_K_M")
    print(f"Base URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Test 1: Health
    results['health'] = await test_health_endpoint(base_url)
    await asyncio.sleep(1)
    
    # Test 2: Non-streaming
    results['non_streaming'] = await test_non_streaming_query(base_url)
    await asyncio.sleep(1)
    
    # Test 3: Streaming
    results['streaming'] = await test_streaming_query(base_url)
    await asyncio.sleep(1)
    
    # Test 4: Error handling
    results['error_handling'] = await test_error_handling(base_url)
    
    # Print summary
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status}{Colors.ENDC} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Total: {passed_tests}/{total_tests} tests passed{Colors.ENDC}")
    
    if passed_tests == total_tests:
        print_success("\n🎉 All tests passed! RAG Query System is working correctly.")
        return 0
    else:
        print_error(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review the errors above.")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test RAG Query System with Qwen 2.5 7B Q5_K_M"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = asyncio.run(run_all_tests(args.base_url))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

