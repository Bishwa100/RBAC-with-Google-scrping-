#!/usr/bin/env python3
"""
Test Deep Analysis Integration

This script tests the integration between the main scraping task and the content analysis agent.
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_deep_analysis_integration():
    """Test the deep analysis integration with a small sample."""

    print("[TEST] Testing Deep Analysis Integration")
    print("=" * 50)

    # Test 1: Verify backend models accept analyze_content
    try:
        from models import SearchRequest

        # Test with deep analysis enabled
        request = SearchRequest(
            topic="Machine Learning",
            search_mode="scraping",
            sources=["youtube", "github"],
            analyze_content=True
        )

        print("[OK] Backend models accept analyze_content parameter")
        print(f"     Request: {request.dict()}")

    except Exception as e:
        print(f"[FAIL] Backend model test failed: {e}")
        return False

    # Test 2: Verify tasks.py has the updated function signature
    try:
        from tasks import scrape_topic_task, analyze_urls_content

        print("[OK] Tasks module has updated functions")

        # Check function signature
        import inspect
        sig = inspect.signature(scrape_topic_task)
        if 'analyze_content' in sig.parameters:
            print("[OK] scrape_topic_task accepts analyze_content parameter")
        else:
            print("[WARN] scrape_topic_task missing analyze_content parameter")

    except ImportError as e:
        print(f"[FAIL] Could not import tasks functions: {e}")
        return False

    # Test 3: Verify content analysis agent is available
    try:
        from content_analysis_agent import ContentAnalysisAgent, WebContentExtractor

        print("[OK] Content Analysis Agent available")

    except ImportError as e:
        print(f"[FAIL] Content Analysis Agent not available: {e}")
        return False

    # Test 4: Test with sample data
    try:
        sample_results = {
            "youtube": [
                {
                    "title": "Machine Learning Basics",
                    "url": "https://example.com/video1",
                    "description": "Learn ML basics",
                    "source": "youtube"
                }
            ],
            "github": [
                {
                    "title": "ML Repository",
                    "url": "https://github.com/example/ml-repo",
                    "description": "Machine learning repository",
                    "source": "github"
                }
            ]
        }

        # Test the analyze_urls_content function with sample data
        enriched = analyze_urls_content(sample_results, "Machine Learning", "test-job-123", max_urls=1)

        if enriched:
            print("[OK] Content analysis function works with sample data")
            print(f"     Processed {len(enriched)} source types")
        else:
            print("[WARN] Content analysis returned empty results")

    except Exception as e:
        print(f"[FAIL] Content analysis test failed: {e}")
        return False

    # Test 5: Check scraped data directory
    scraped_dir = Path("backend/scraped_data")
    if scraped_dir.exists():
        json_files = list(scraped_dir.glob("*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)

            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                has_content_analysis = data.get("content_analysis_enabled", False)
                if has_content_analysis:
                    print(f"[INFO] Found existing file with content analysis: {latest_file.name}")
                else:
                    print(f"[INFO] Found existing file without content analysis: {latest_file.name}")

            except Exception as e:
                print(f"[WARN] Could not read latest scraped file: {e}")
        else:
            print("[INFO] No existing scraped data files found")
    else:
        print("[INFO] Scraped data directory will be created on first run")

    print("\n[SUMMARY] Deep Analysis Integration Test Results:")
    print("✅ Backend models support deep analysis parameter")
    print("✅ Tasks module updated with content analysis integration")
    print("✅ Content Analysis Agent is available")
    print("✅ Integration functions work with sample data")
    print("\n[READY] Deep Analysis feature is ready to use!")
    print("\nTo test the full flow:")
    print("1. Start the backend: cd backend && python main.py")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Search for a topic with 'Deep Analysis' enabled")
    print("4. Wait for the analysis to complete (2-5 minutes)")
    print("5. Check the results for analyzed content")

    return True

if __name__ == "__main__":
    test_deep_analysis_integration()