#!/usr/bin/env python3
"""
Filter words for polygon boundaries.

This script loads a curated word list and filters it by the UK/Ireland polygon,
marking out-of-bounds coordinates as INVALID_POINT. This matches the logic from
the old generate_word_list.py script.
"""

import os
import argparse
from twowords_utils.polygon_utils import PolygonUtils
from twowords_utils.zip_utils import ZipUtils

def main():
    parser = argparse.ArgumentParser(description="Filter words by UK/Ireland polygon")
    parser.add_argument("--input-file", default=None, help="Input words file")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--root-dir", default=None, help="Root directory")
    
    args = parser.parse_args()
    
    # Determine paths based on environment
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        root_dir = args.root_dir or "/"
        output_dir = args.output_dir or "/output"
        input_file = args.input_file or "/output/words.txt"
        output_zip = "/expanded_words.zip"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = args.root_dir or os.path.dirname(os.path.dirname(script_dir))
        output_dir = args.output_dir or os.path.join(root_dir, "data", "output")
        input_file = args.input_file or os.path.join(output_dir, "words.txt")
        output_zip = os.path.join(root_dir, "expanded_words.zip")
    
    print("TwoWords API - Polygon Filtering")
    print("=" * 50)
    print(f"Root directory: {root_dir}")
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    
    # Check input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("Please run word curation first.")
        return 1
    
    # Load base words
    with open(input_file, "r", encoding="utf-8") as f:
        base_words = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(base_words)} base words")
    
    # Filter by polygon
    polygon_utils = PolygonUtils(root_dir)
    filtered_words = polygon_utils.filter_words_for_polygon(base_words)
    
    # Save filtered results
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "words.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_words))
    
    print(f"Filtered word list written to {output_file}")
    
    # Create expanded_words.zip in the root (matches old behavior)
    ZipUtils.create_words_zip(output_file, output_zip)
    
    # Statistics
    valid_words = [w for w in filtered_words if w != "INVALID_POINT"]
    invalid_count = len(filtered_words) - len(valid_words)
    print(f"\nFiltering Statistics:")
    print(f"  Total positions: {len(filtered_words):,}")
    print(f"  Valid positions: {len(valid_words):,}")
    print(f"  Invalid positions: {invalid_count:,}")
    print(f"  Valid percentage: {len(valid_words)/len(filtered_words)*100:.1f}%")
    
    # Show sample of valid words for verification
    sample_words = [w for w in filtered_words[:100] if w != "INVALID_POINT"][:10]
    if sample_words:
        print(f"Sample valid words: {sample_words}")
    
    return 0

if __name__ == "__main__":
    exit(main())
