#!/usr/bin/env python3
"""
Optimize word list to place the best words at high-population indices.

This script mirrors the functionality of the old score_words.py script and uses 
the enhanced word curation utilities to create an optimized word list.
"""

import os
import argparse
from twowords_utils.word_popularity import WordPopularity

def optimize_words(words_dir=None, output_dir=None):
    """Optimize word list for population centers without command line parsing."""
    
    # Determine paths based on environment
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_dir = words_dir or "/words"
        output_dir = output_dir or "/output"
    else:
        # Running locally - get repo root and set paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        words_dir = words_dir or os.path.join(repo_root, "data", "words")
        output_dir = output_dir or os.path.join(repo_root, "data", "output")
    
    print("TwoWords API - Word List Optimizer")
    print("=" * 50)
    print(f"Words directory: {words_dir}")
    print(f"Output directory: {output_dir}")
    
    # Read the filtered words from the previous step
    filtered_words_file = os.path.join(output_dir, "words.txt")
    if not os.path.exists(filtered_words_file):
        raise FileNotFoundError(f"Filtered words file not found: {filtered_words_file}")
    
    print(f"Loading filtered words from: {filtered_words_file}")
    with open(filtered_words_file, 'r', encoding='utf-8') as f:
        all_words = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(all_words):,} filtered words")
    
    # Create word popularity analyzer and optimize the word placement
    word_pop = WordPopularity(words_dir)
    optimized_words = word_pop.optimize_word_placement(all_words)
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "words.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in optimized_words:
            f.write(f"{word}\n")
    
    print(f"\nSaved optimized word list to {output_file}")
    print(f"Total words: {len(optimized_words):,}")
    
    # Show sample results
    print(f"\nFirst 20 words: {optimized_words[:20]}")
    
    # Statistics
    lengths = [len(word) for word in optimized_words[:1000]]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    print(f"\nWord quality (first 1000 words):")
    print(f"  Average length: {avg_length:.1f} characters")
    print(f"  Short words (≤4 chars): {sum(1 for l in lengths if l <= 4)}")
    print(f"  Medium words (5-7 chars): {sum(1 for l in lengths if 5 <= l <= 7)}")
    print(f"  Long words (8+ chars): {sum(1 for l in lengths if l >= 8)}")

def main():
    parser = argparse.ArgumentParser(description="Optimize word list for population centers")
    parser.add_argument("--words-dir", default=None, help="Directory containing word files")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    
    args = parser.parse_args()
    
    optimize_words(args.words_dir, args.output_dir)

if __name__ == "__main__":
    main()
