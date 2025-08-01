#!/usr/bin/env python3
"""
Verify that the coordinate-to-word mapping is working correctly.

This script validates that the word mapping system produces consistent results
and that important indices contain the expected high-quality words.
"""

import os
import argparse
from twowords_utils.polygon_utils import PolygonUtils

def index_to_lat(index: int) -> float:
    """Convert latitude index back to latitude value."""
    LAT_MIN = 49.0
    STEP = 0.0001
    return LAT_MIN + index * STEP

def index_to_lon(index: int) -> float:
    """Convert longitude index back to longitude value."""
    LON_MIN = -8.0
    STEP = 0.0001
    return LON_MIN + index * STEP

def load_important_indices(filepath: str) -> set:
    """Load important indices from file."""
    indices = set()
    if not os.path.exists(filepath):
        return indices
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                indices.add(int(line))
    return indices

def main():
    parser = argparse.ArgumentParser(description="Verify coordinate-to-word mapping correctness")
    parser.add_argument("--words-dir", default=None, help="Directory containing word files")
    parser.add_argument("--output-dir", default=None, help="Directory containing output files")
    
    args = parser.parse_args()
    
    # Determine paths based on environment
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_dir = args.words_dir or "/words"
        output_dir = args.output_dir or "/output"
        repo_root = "/"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        words_dir = args.words_dir or os.path.join(repo_root, "data", "words")
        output_dir = args.output_dir or os.path.join(repo_root, "data", "output")
    
    print("TwoWords API - Mapping Verification")
    print("=" * 50)
    
    # Load words list
    words_file = os.path.join(output_dir, "words.txt")
    if not os.path.exists(words_file):
        print(f"Error: Words file not found at {words_file}")
        print("Please run the word generation pipeline first.")
        return 1
    
    with open(words_file, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(words):,} words from {words_file}")
    
    # Load important indices
    important_indices_file = os.path.join(words_dir, "important_indices.txt")
    important_indices = load_important_indices(important_indices_file)
    print(f"Loaded {len(important_indices)} important indices")
    
    # Verify mapping consistency
    print("\nVerifying mapping consistency...")
    
    # Test a few specific coordinates
    test_coordinates = [
        (51.5074, -0.1278, "London"),
        (53.4808, -2.2426, "Manchester"), 
        (55.8642, -4.2518, "Glasgow"),
        (51.4545, -2.5879, "Bristol"),
    ]
    
    polygon_utils = PolygonUtils(repo_root)
    
    for lat, lon, city in test_coordinates:
        lat_idx = int((lat - 49.0) / 0.0001)
        lon_idx = int((lon - (-8.0)) / 0.0001)
        
        # Use max index to get the word (same logic as the C# API)
        max_idx = max(lat_idx, lon_idx)
        
        if max_idx < len(words):
            word = words[max_idx]
            print(f"  {city:10s}: lat={lat:8.4f} (idx={lat_idx:6d}), lon={lon:8.4f} (idx={lon_idx:6d}) -> max_idx={max_idx:6d} -> '{word}'")
        else:
            print(f"  {city:10s}: lat={lat:8.4f} (idx={lat_idx:6d}), lon={lon:8.4f} (idx={lon_idx:6d}) -> max_idx={max_idx:6d} -> INDEX OUT OF RANGE")
    
    # Check what words are at important indices
    print(f"\nWords at important indices (first 20):")
    important_indices_list = sorted(list(important_indices))
    
    for i, idx in enumerate(important_indices_list[:20]):
        if idx < len(words):
            word = words[idx]
            lat = index_to_lat(idx) if idx < 110001 else None
            lon = index_to_lon(idx) if idx < 100001 else None
            coord_type = "latitude" if lat and idx < 110001 else "longitude" if lon and idx < 100001 else "unknown"
            print(f"  Index {idx:6d} ({coord_type:9s}): '{word}'")
        else:
            print(f"  Index {idx:6d}: OUT OF RANGE")
    
    # Statistics
    valid_words = [w for w in words if w != "INVALID_POINT"]
    invalid_count = len(words) - len(valid_words)
    
    print(f"\nMapping Statistics:")
    print(f"  Total positions: {len(words):,}")
    print(f"  Valid words: {len(valid_words):,}")
    print(f"  Invalid positions: {invalid_count:,}")
    print(f"  Valid percentage: {len(valid_words)/len(words)*100:.1f}%")
    
    # Word quality at important indices
    important_words = [words[idx] for idx in important_indices if idx < len(words) and words[idx] != "INVALID_POINT"]
    if important_words:
        avg_length = sum(len(w) for w in important_words) / len(important_words)
        print(f"\nImportant indices word quality:")
        print(f"  Valid words at important indices: {len(important_words)}")
        print(f"  Average length: {avg_length:.1f} characters")
        print(f"  Sample words: {important_words[:10]}")
    
    print("\nVerification complete!")
    return 0

if __name__ == "__main__":
    exit(main())
