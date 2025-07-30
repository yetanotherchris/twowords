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

def load_food_dishes() -> List[str]:
    """Load food dishes from the word-data directory for priority placement."""
    try:
        with open('../word-data/food_dishes_final.txt', 'r', encoding='utf-8') as f:
            dishes = [line.strip().lower() for line in f if line.strip()]
        return dishes
    except FileNotFoundError:
        print("Warning: food_dishes_final.txt not found, skipping food priority")
        return []

def load_important_indices(file_path: str) -> Set[int]:
    """Load the pre-calculated important indices for major population centers."""
    indices = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    indices.add(int(line))
    except FileNotFoundError:
        # Try the word-data directory
        with open('../word-data/important_indices.txt', 'r') as f:
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

def calculate_word_score(word: str, food_dishes: Set[str]) -> WordScore:
    """Calculate a desirability score for a word (higher = better)."""
    length = len(word)
    is_common = is_common_word(word)
    is_simple = is_simple_word(word)
    is_food = word in food_dishes
    
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
    
    # Food dishes get high priority for populated areas
    if is_food:
        score += 60  # Higher than common words bonus
    
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

def optimize_word_list(words: List[str], important_indices: Set[int], food_dishes: List[str]) -> List[str]:
    """Create an optimized word list with food dishes at important indices."""
    print(f"Optimizing {len(words):,} words for {WORDS_NEEDED:,} positions...")
    print(f"Food dishes available: {len(food_dishes)}")
    
    food_set = set(food_dishes)
    
    # Score all words
    print("Scoring words by desirability...")
    scored_words = [calculate_word_score(word, food_set) for word in words]
    
    # Sort by score (best first)
    scored_words.sort(key=lambda x: x.score, reverse=True)
    
    # Separate food dishes from other words for strategic placement
    food_words = [sw for sw in scored_words if sw.word in food_set]
    non_food_words = [sw for sw in scored_words if sw.word not in food_set]
    
    print(f"Food dishes found: {len(food_words)}")
    print(f"Best food dishes: {[fw.word for fw in food_words[:20]]}")
    print(f"Important indices count: {len(important_indices)}")
    
    # Create the optimized list - initialize with placeholder words
    optimized = ['placeholder'] * WORDS_NEEDED
    used_words = set()
    
    # FIRST: Place the best FOOD DISHES at ALL important population indices
    important_indices_list = sorted(list(important_indices))
    print(f"Placing FOOD DISHES at {len(important_indices_list)} important indices...")
    
    for i, idx in enumerate(important_indices_list):
        if idx < WORDS_NEEDED and i < len(food_words):
            word = food_words[i].word
            optimized[idx] = word
            used_words.add(word)
            print(f"  Index {idx:6d}: '{word}' (food dish, score: {food_words[i].score:.1f})")
        elif idx < WORDS_NEEDED:
            # Fallback to best non-food word if we run out of food dishes (shouldn't happen)
            word = non_food_words[0].word
            optimized[idx] = word
            used_words.add(word)
            print(f"  Index {idx:6d}: '{word}' (fallback, score: {non_food_words[0].score:.1f})")
    
    # SECOND: Fill all remaining positions with the best unused words (food + non-food)
    print("Filling remaining positions with best unused words...")
    remaining_words = [sw.word for sw in scored_words if sw.word not in used_words]
    
    fill_index = 0
    for pos in range(WORDS_NEEDED):
        if optimized[pos] == 'placeholder':  # Position not filled yet
            if fill_index < len(remaining_words):
                optimized[pos] = remaining_words[fill_index]
                fill_index += 1
            else:
                # Fallback if we run out (shouldn't happen)
                optimized[pos] = f"word{pos}"
    
    # Verify no placeholder positions remain
    placeholders = [i for i, word in enumerate(optimized) if word == 'placeholder']
    if placeholders:
        print(f"Warning: {len(placeholders)} placeholder positions remain!")
    
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
    print("Loading words from word-data/expanded_words.txt...")
    try:
        with open('../word-data/expanded_words.txt', 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("expanded_words.txt not found in word-data, trying zip file...")
        words = load_words_from_zip('../expanded_words.zip')
    print(f"Loaded {len(words):,} words")
    
    # Load food dishes for priority placement
    print("Loading food dishes for priority placement...")
    food_dishes = load_food_dishes()
    print(f"Loaded {len(food_dishes)} food dishes")
    
    # Load important indices
    print("Loading important population indices...")
    important_indices = load_important_indices('important_indices.txt')
    print(f"Loaded {len(important_indices)} important indices")
    
    # Optimize the word list
    optimized_words = optimize_word_list(words, important_indices, food_dishes)
    
    # Save results
    output_file = 'optimized_words.txt'
    save_optimized_words(optimized_words, output_file)
    print(f"Saved optimized word list to {output_file}")
    
    # Show some statistics
    print("\nOptimization Results:")
    print(f"Total words in optimized list: {len(optimized_words):,}")
    
    # Sample what words are at important indices
    print(f"\nFOOD DISHES at major population centres:")
    important_list = sorted(list(important_indices))[:15]  # Show first 15
    food_set = set(food_dishes)
    for idx in important_list:
        if idx < len(optimized_words):
            word = optimized_words[idx]
            is_food = word in food_set
            status = "🍽️ FOOD" if is_food else "❌ NON-FOOD"
            print(f"  Index {idx:6d}: '{word}' {status}")
    
    # Check food dishes usage at important indices
    important_words = [optimized_words[idx] for idx in important_indices if idx < len(optimized_words)]
    food_at_important = sum(1 for word in important_words if word in food_set)
    print(f"\nFood dishes at important indices: {food_at_important}/{len(important_words)} ({food_at_important/len(important_words)*100:.1f}%)")
    
    # Check overall food dishes usage
    food_count = sum(1 for word in optimized_words[:1000] if word in food_set)
    print(f"Food dishes in top 1000 positions: {food_count}")
    
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
