#!/usr/bin/env python3
"""
Optimize word list to place the best words at high-population indices.

This script:
1. Loads the million+ word list from expanded_words.zip
2. Scores words by desirability (length, commonality, simplicity)
3. Places the best words at indices for major UK population centers
4. Creates an optimized list of exactly 110,001 words
"""

import zipfile
import re
from collections import Counter
from dataclasses import dataclass
from typing import List, Set

# Constants from the API
WORDS_NEEDED = 110001

@dataclass
class WordScore:
    word: str
    score: float
    length: int
    is_common: bool
    is_simple: bool

def load_words_from_zip(zip_path: str) -> List[str]:
    """Load words from the expanded_words.zip file."""
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        with zip_file.open('expanded_words.txt') as f:
            lines = f.read().decode('utf-8').strip().split('\n')
            words = [line.strip().lower() for line in lines if line.strip()]
    return words

def load_important_indices(file_path: str) -> Set[int]:
    """Load the pre-calculated important indices for major population centers."""
    indices = set()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                indices.add(int(line))
    return indices

def is_common_word(word: str) -> bool:
    """Check if word is a common English word."""
    # Common word patterns and high-frequency words
    common_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'you', 'your', 'have', 'had', 'this',
        'but', 'his', 'her', 'she', 'or', 'if', 'we', 'my', 'me', 'all',
        'up', 'out', 'so', 'can', 'get', 'go', 'new', 'now', 'old', 'see',
        'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say',
        'she', 'too', 'use', 'big', 'car', 'cat', 'dog', 'eye', 'far',
        'few', 'got', 'her', 'him', 'how', 'man', 'may', 'not', 'oil',
        'one', 'our', 'own', 'run', 'sun', 'top', 'try', 'yet', 'yes'
    }
    
    # Check if it's in our common words list
    if word in common_words:
        return True
    
    # Common prefixes/suffixes that might indicate common words
    common_patterns = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion']
    if len(word) <= 6 and any(word.endswith(pattern) for pattern in common_patterns):
        return True
        
    return False

def is_simple_word(word: str) -> bool:
    """Check if word uses simple characters and patterns."""
    # Only contains basic letters (no special characters, numbers)
    if not re.match(r'^[a-z]+$', word):
        return False
    
    # Avoid words with unusual letter combinations
    difficult_patterns = [
        'qq', 'xx', 'zz', 'uu', 'ii', 'oo',  # Double unusual letters
        'xh', 'xk', 'xj', 'qw', 'qy',        # Unusual combinations
        'ght', 'pht', 'rht',                  # Complex consonant clusters
    ]
    
    return not any(pattern in word for pattern in difficult_patterns)

def calculate_word_score(word: str) -> WordScore:
    """Calculate a desirability score for a word (higher = better)."""
    length = len(word)
    is_common = is_common_word(word)
    is_simple = is_simple_word(word)
    
    # Base score starts higher for shorter words
    score = 100.0
    
    # Length penalty (prefer shorter words)
    if length <= 3:
        score += 50  # Very short words get bonus
    elif length <= 5:
        score += 20  # Short words get bonus
    elif length <= 7:
        score += 0   # Medium words neutral
    elif length <= 10:
        score -= 20  # Long words get penalty
    else:
        score -= 50  # Very long words get big penalty
    
    # Common word bonus
    if is_common:
        score += 40
    
    # Simple word bonus
    if is_simple:
        score += 20
    
    # Avoid single letters except a few
    if length == 1 and word not in ['a', 'i']:
        score -= 30
    
    return WordScore(word, score, length, is_common, is_simple)

def optimize_word_list(words: List[str], important_indices: Set[int]) -> List[str]:
    """Create an optimized word list with best words at important indices."""
    print(f"Optimizing {len(words):,} words for {WORDS_NEEDED:,} positions...")
    
    # Score all words
    print("Scoring words by desirability...")
    scored_words = [calculate_word_score(word) for word in words]
    
    # Sort by score (best first)
    scored_words.sort(key=lambda x: x.score, reverse=True)
    
    # Take the best words we need
    best_words = [sw.word for sw in scored_words[:WORDS_NEEDED]]
    
    print(f"Selected top {len(best_words):,} words")
    print(f"Best words sample: {best_words[:20]}")
    print(f"Important indices count: {len(important_indices)}")
    
    # Create the optimized list
    optimized = [''] * WORDS_NEEDED
    used_words = set()
    
    # First, place the very best words at important indices
    important_indices_list = sorted(list(important_indices))
    for i, idx in enumerate(important_indices_list):
        if idx < WORDS_NEEDED and i < len(best_words):
            optimized[idx] = best_words[i]
            used_words.add(best_words[i])
    
    # Fill remaining positions with remaining good words
    word_idx = 0
    for pos in range(WORDS_NEEDED):
        if optimized[pos] == '':  # Position not filled yet
            # Find next unused word
            while word_idx < len(best_words) and best_words[word_idx] in used_words:
                word_idx += 1
            if word_idx < len(best_words):
                optimized[pos] = best_words[word_idx]
                used_words.add(best_words[word_idx])
                word_idx += 1
    
    # Verify no empty positions
    empty_positions = [i for i, word in enumerate(optimized) if word == '']
    if empty_positions:
        print(f"Warning: {len(empty_positions)} empty positions found")
    
    return optimized

def save_optimized_words(words: List[str], output_path: str):
    """Save the optimized word list."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")

def main():
    print("TwoWords API - Word List Optimizer")
    print("=" * 50)
    
    # Load current words
    print("Loading words from expanded_words.zip...")
    words = load_words_from_zip('../expanded_words.zip')
    print(f"Loaded {len(words):,} words")
    
    # Load important indices
    print("Loading important population indices...")
    important_indices = load_important_indices('important_indices.txt')
    print(f"Loaded {len(important_indices)} important indices")
    
    # Optimize the word list
    optimized_words = optimize_word_list(words, important_indices)
    
    # Save results
    output_file = 'optimized_words.txt'
    save_optimized_words(optimized_words, output_file)
    print(f"Saved optimized word list to {output_file}")
    
    # Show some statistics
    print("\nOptimization Results:")
    print(f"Total words in optimized list: {len(optimized_words):,}")
    
    # Sample what words are at important indices
    print(f"\nWords at major population centers:")
    important_list = sorted(list(important_indices))[:10]  # Show first 10
    for idx in important_list:
        if idx < len(optimized_words):
            print(f"  Index {idx:6d}: '{optimized_words[idx]}'")
    
    # Show length distribution
    lengths = [len(word) for word in optimized_words[:1000]]
    avg_length = sum(lengths) / len(lengths)
    print(f"\nWord quality (first 1000 words):")
    print(f"  Average length: {avg_length:.1f} characters")
    print(f"  Short words (≤4 chars): {sum(1 for l in lengths if l <= 4)}")
    print(f"  Medium words (5-7 chars): {sum(1 for l in lengths if 5 <= l <= 7)}")
    print(f"  Long words (8+ chars): {sum(1 for l in lengths if l >= 8)}")

if __name__ == "__main__":
    main()
