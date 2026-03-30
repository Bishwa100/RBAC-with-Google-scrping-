#!/usr/bin/env python3
"""
Scraped Data Viewer - View and analyze scraped data files
"""
import json
import os
from pathlib import Path
from datetime import datetime
import sys


def list_data_files(directory):
    """List all JSON files in the scraped data directory."""
    data_dir = Path(directory)
    if not data_dir.exists():
        print(f"Directory {directory} does not exist yet.")
        return []

    json_files = sorted(data_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    return json_files


def display_file_info(filepath):
    """Display summary information about a scraped data file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n{'='*80}")
        print(f"File: {filepath.name}")
        print(f"{'='*80}")

        # Check if it's a main orchestration file
        if "topic" in data:
            # Main orchestration output
            print(f"Type: Main Orchestration Results")
            print(f"Topic: {data.get('topic', 'N/A')}")
            print(f"Search Mode: {data.get('search_mode', 'N/A')}")
            print(f"Total Results: {data.get('total_results', 0)}")

            if "counts" in data:
                print(f"\nResults by Source:")
                for source, count in data.get("counts", {}).items():
                    print(f"  - {source.capitalize()}: {count}")

            if "insights" in data:
                print(f"\nInsights Summary:")
                print(f"  {data['insights'].get('summary', 'N/A')[:200]}...")

            if "error" in data:
                print(f"\n⚠️  Error: {data['error']}")

        else:
            print(f"Type: Unknown format")
            print(f"Keys: {', '.join(data.keys())}")

        print(f"\n{'='*80}\n")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {filepath.name}: {e}")
    except Exception as e:
        print(f"Error reading file {filepath.name}: {e}")


def show_latest(directory, count=5):
    """Show the latest scraped data files."""
    json_files = list_data_files(directory)

    if not json_files:
        print(f"No scraped data files found in {directory}")
        return

    print(f"\n{'='*80}")
    print(f"Latest {min(count, len(json_files))} files in {directory}:")
    print(f"{'='*80}")

    for i, filepath in enumerate(json_files[:count], 1):
        mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        print(f"{i}. {filepath.name}")
        print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {filepath.stat().st_size / 1024:.2f} KB")
        print()


def main():
    """Main function."""
    # Define directories
    backend_dir = Path(__file__).parent / "backend" / "scraped_data"

    print("\n" + "="*80)
    print("SCRAPED DATA VIEWER")
    print("="*80)

    if len(sys.argv) > 1:
        # If a file path is provided, show details
        filepath = Path(sys.argv[1])
        if filepath.exists():
            display_file_info(filepath)
        else:
            print(f"File not found: {filepath}")
        return

    # Show latest from scraped data directory
    print("\n📊 MAIN ORCHESTRATION RESULTS")
    show_latest(backend_dir, count=5)

    # Interactive mode
    print("\nOptions:")
    print("1. View details of a specific file (enter file number)")
    print("2. View all files in backend/scraped_data")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        all_files = list_data_files(backend_dir)
        if not all_files:
            print("No files available.")
            return

        print("\nAvailable files:")
        for i, f in enumerate(all_files, 1):
            print(f"{i}. {f.name}")

        try:
            file_num = int(input("\nEnter file number: ").strip())
            if 1 <= file_num <= len(all_files):
                display_file_info(all_files[file_num - 1])
            else:
                print("Invalid file number.")
        except ValueError:
            print("Invalid input.")

    elif choice == "2":
        files = list_data_files(backend_dir)
        for f in files:
            display_file_info(f)

    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
