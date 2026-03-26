#!/usr/bin/env python3
"""
Quick Content Analysis Runner

This script provides a simple way to run content analysis on your latest scraped data.
It integrates with the existing topicLens system and uses your local Ollama model.

Usage:
  python run_content_analysis.py                    # Analyze latest scraped data
  python run_content_analysis.py path/to/file.json  # Analyze specific file
  python run_content_analysis.py --help             # Show help

Features:
- Automatically finds your latest scraped data file
- Uses your local Ollama model for intelligent analysis
- Extracts content from all types of websites (YouTube, GitHub, Reddit, etc.)
- Generates comprehensive insights with relevance scores, quality ratings, and more
- Saves enriched results with full analysis data
"""

import sys
import os
import argparse
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def main():
    parser = argparse.ArgumentParser(
        description="Run content analysis on scraped data using local Ollama model"
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Scraped data JSON file to analyze (default: auto-detect latest)'
    )
    parser.add_argument(
        '--max-urls',
        type=int,
        help='Maximum number of URLs to analyze (default: unlimited)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Number of parallel workers (default: 3)'
    )

    args = parser.parse_args()

    # Import the content analysis agent
    try:
        from content_analysis_agent import ContentAnalysisAgent
        print("✅ Content Analysis Agent loaded successfully")
    except ImportError as e:
        print(f"❌ Could not load Content Analysis Agent: {e}")
        print("Make sure you're running this from the topicLens directory")
        return 1

    # Find the file to analyze
    if args.file:
        scraped_file = args.file
    else:
        # Auto-detect latest file
        scraped_dir = Path("backend/scraped_data")
        if not scraped_dir.exists():
            print("❌ No scraped data directory found. Please run scraping first.")
            print("Use: python backend/tasks.py or the web interface")
            return 1

        json_files = [f for f in scraped_dir.glob("*.json") if "ANALYZED" not in f.name]
        if not json_files:
            print("❌ No scraped data files found in backend/scraped_data/")
            print("Please run scraping first to generate data to analyze.")
            return 1

        scraped_file = str(max(json_files, key=lambda x: x.stat().st_mtime))
        print(f"🔍 Auto-detected latest scraped file: {scraped_file}")

    if not os.path.exists(scraped_file):
        print(f"❌ File not found: {scraped_file}")
        return 1

    # Initialize and run agent
    print("🤖 Initializing Content Analysis Agent...")
    agent = ContentAnalysisAgent()

    # Set max workers if specified
    if hasattr(agent, 'max_workers'):
        agent.max_workers = args.workers

    print(f"🚀 Starting analysis...")
    print(f"📁 Input file: {scraped_file}")
    if args.max_urls:
        print(f"🎯 Max URLs: {args.max_urls}")
    else:
        print(f"🎯 Max URLs: unlimited")

    # Run analysis
    enriched_data = agent.analyze_scraped_data(scraped_file, args.max_urls)

    if enriched_data:
        # Save results
        output_file = agent.save_results(enriched_data)
        if output_file:
            print(f"\n🎉 SUCCESS! Analysis complete.")
            print(f"📄 Results: {output_file}")
            print(f"📋 Summary: {output_file.replace('.json', '_SUMMARY.json')}")
            return 0
        else:
            print("❌ Failed to save results")
            return 1
    else:
        print("❌ Analysis failed")
        return 1


if __name__ == "__main__":
    exit(main())