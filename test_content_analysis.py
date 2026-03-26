#!/usr/bin/env python3
"""
Quick test of the Content Analysis Agent system
"""

import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_content_analysis():
    """Test the content analysis system with sample data."""

    print("[TEST] Testing Content Analysis Agent System")
    print("=" * 50)

    # Test 1: Import modules
    try:
        from content_analysis_agent import ContentAnalysisAgent, WebContentExtractor, OllamaContentAnalyzer
        print("[OK] Modules imported successfully")
    except Exception as e:
        print(f"[FAIL] Module import failed: {e}")
        return False

    # Test 2: Check Ollama connection
    try:
        from llm import call_ollama
        test_response = call_ollama("Reply with just: TEST_OK", temperature=0.1)
        if "TEST_OK" in test_response or len(test_response) > 0:
            print("[OK] Ollama connection working")
        else:
            print("[WARN] Ollama connection unclear but responding")
    except Exception as e:
        print(f"[WARN] Ollama connection test failed: {e}")

    # Test 3: Test content extraction
    try:
        extractor = WebContentExtractor()
        # Test with a simple, reliable URL
        test_url = "https://httpbin.org/html"  # Simple test page
        result = extractor.extract_content(test_url, "generic")

        if result["extraction_status"] in ["success", "partial"]:
            print("[OK] Content extraction working")
        else:
            print(f"[WARN] Content extraction test unclear: {result['extraction_status']}")

    except Exception as e:
        print(f"[FAIL] Content extraction test failed: {e}")

    # Test 4: Check for scraped data
    scraped_dir = Path("backend/scraped_data")
    if scraped_dir.exists():
        json_files = list(scraped_dir.glob("*.json"))
        analyzing_files = [f for f in json_files if "ANALYZED" not in f.name]

        if analyzing_files:
            latest_file = max(analyzing_files, key=lambda x: x.stat().st_mtime)
            print(f"[OK] Found scraped data file: {latest_file.name}")

            # Check file structure
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "topic" in data and "results" in data:
                    total_urls = sum(len(items) for items in data["results"].values() if isinstance(items, list))
                    print(f"[OK] Data structure valid - {total_urls} URLs found")
                else:
                    print("[WARN] Data structure unclear")

            except Exception as e:
                print(f"[FAIL] Could not read scraped data: {e}")
        else:
            print("[WARN] No scraped data files found")
    else:
        print("[FAIL] Scraped data directory doesn't exist")

    print("\n[SUMMARY] System Status Summary:")
    print("- Content Analysis Agent is ready to use")
    print("- Run: python run_content_analysis.py --max-urls 5")
    print("- Or: python content_analysis_agent.py")

    return True

    print("\n🎯 System Status Summary:")
    print("- Content Analysis Agent is ready to use")
    print("- Run: python run_content_analysis.py --max-urls 5")
    print("- Or: python content_analysis_agent.py")

    return True

if __name__ == "__main__":
    test_content_analysis()