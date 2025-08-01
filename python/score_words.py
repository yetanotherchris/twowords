#!/usr/bin/env python3
"""
Optimize word list to place the best words at high-population indices.

This script:
1. Loads the million+ word list from expanded_words.zip
2. Scores words by desirability (length, commonality, simplicity)
3. Places the best words at indices for major UK population centers
4. Creates an optimized list of exactly 110,001 words
"""

import os
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

def is_valid_english_word(word: str) -> bool:
    """Check if word looks like a proper English word."""
    # Must have vowels (except very short common words)
    if len(word) > 2 and not any(c in word for c in 'aeiou'):
        return False
    
    # Reject obvious abbreviations
    if len(word) <= 4 and word.isupper():
        return False
    
    # Reject words with too many consonants in a row
    consonant_count = 0
    for char in word:
        if char not in 'aeiou':
            consonant_count += 1
            if consonant_count > 3:  # No more than 3 consonants in a row
                return False
        else:
            consonant_count = 0
    
    # Reject words with unusual letter combinations
    bad_patterns = ['qq', 'zz', 'xx', 'bv', 'cj', 'cv', 'cw', 'dx', 'fq', 'fx', 'gq', 'gx', 'hx', 'jf', 'jg', 'jq', 'jv', 'jw', 'jx', 'jz', 'kq', 'kx', 'mx', 'px', 'qc', 'qf', 'qg', 'qh', 'qj', 'qk', 'ql', 'qm', 'qn', 'qp', 'qr', 'qs', 'qt', 'qv', 'qw', 'qx', 'qy', 'qz', 'sx', 'vb', 'vf', 'vh', 'vj', 'vm', 'vp', 'vq', 'vt', 'vw', 'vx', 'wq', 'wx', 'xf', 'xj', 'xk', 'xm', 'xp', 'xq', 'xv', 'xw', 'xz', 'zx']
    for pattern in bad_patterns:
        if pattern in word:
            return False
    
    # Reject single letters except common ones
    if len(word) == 1 and word not in ['a', 'i']:
        return False
    
    # Reject very short words that look like abbreviations
    if len(word) <= 3 and any(char.isupper() for char in word):
        return False
    
    # Must end with a vowel or common consonant ending
    if len(word) > 3 and word[-1] not in 'aeiouynslrdtmh':
        return False
    
    return True

def load_words_from_zip(zip_path: str) -> List[str]:
    """Load words from curated English word lists in word-data directory."""
    
    # Try to load from Peter Norvig's curated English word list (highest quality)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    word_data_dir = os.path.join(script_dir, 'word-data')
    norvig_file = os.path.join(word_data_dir, 'norvig-word-list.txt')
    try:
        with open(norvig_file, 'r', encoding='utf-8') as f:
            norvig_words = [line.strip().lower() for line in f if line.strip()]
        
        # Apply basic filtering to Norvig's already-clean list
        filtered_words = []
        for word in norvig_words:
            # Keep words in a reasonable range for memorability
            if len(word) < 2 or len(word) > 10:
                continue
            
            # Basic validation (Norvig's list should already be clean)
            if not is_valid_english_word(word):
                continue
                
            filtered_words.append(word)
        
        print(f"Loaded {len(filtered_words):,} quality English words from Norvig's curated list")
        return filtered_words
        
    except FileNotFoundError:
        print(f"Norvig word list not found: {norvig_file}")
        print("Falling back to zip file...")
    
    # Fallback to zip file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Look for the first text file in the zip
            text_files = [f for f in zip_file.namelist() if f.endswith('.txt')]
            if not text_files:
                raise FileNotFoundError("No text files found in zip")
            
            with zip_file.open(text_files[0]) as f:
                lines = f.read().decode('utf-8').strip().split('\n')
                words = [line.strip().lower() for line in lines if line.strip()]
                
        # Apply strict filtering to zip file words
        filtered_words = []
        for word in words:
            if len(word) < 2 or len(word) > 10:
                continue
            if not is_valid_english_word(word):
                continue
            if not is_clearly_english_word(word):
                continue
            filtered_words.append(word)
        
        print(f"Fallback: loaded {len(filtered_words):,} filtered words from zip file")
        return filtered_words
        
    except Exception as e:
        print(f"Error loading from zip file: {e}")
        raise FileNotFoundError("No word sources available")

def is_clearly_english_word(word: str) -> bool:
    """Additional strict validation for clearly English words."""
    # Must have reasonable vowel distribution
    vowels = sum(1 for c in word if c in 'aeiou')
    if len(word) > 3 and vowels == 0:
        return False
    
    # Check for reasonable vowel ratio
    vowel_ratio = vowels / len(word)
    if vowel_ratio < 0.2 or vowel_ratio > 0.7:  # Between 20% and 70% vowels
        return False
    
    # Reject words that look like proper names or abbreviations
    if word[0].isupper():
        return False
    
    # Reject words with repeated unusual patterns
    if any(pattern * 2 in word for pattern in ['aa', 'ii', 'oo', 'uu']):
        return False
    
    # Must not look like an abbreviation or code
    consonant_clusters = ['bcf', 'bch', 'bdl', 'bdr', 'bgl', 'bkc', 'bkg', 'bkl', 'bkp', 'bkt', 'cpt', 'ctn', 'ctx', 'cwt', 'dbl', 'dft', 'dgr', 'dpt', 'dvt', 'frt', 'gln', 'grd', 'hwy', 'inc', 'ltd', 'mfg', 'mgr', 'pkg', 'pkt', 'plt', 'pnt', 'qty', 'rpt', 'sgt', 'spl', 'std', 'str', 'tbl', 'tmp', 'wgt']
    if any(cluster in word for cluster in consonant_clusters):
        return False
    
    return True

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
    # Expanded common word patterns and high-frequency words
    common_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'you', 'your', 'have', 'had', 'this',
        'but', 'his', 'her', 'she', 'or', 'if', 'we', 'my', 'me', 'all',
        'up', 'out', 'so', 'can', 'get', 'go', 'new', 'now', 'old', 'see',
        'two', 'way', 'who', 'boy', 'did', 'let', 'put', 'say',
        'too', 'use', 'big', 'car', 'cat', 'dog', 'eye', 'far',
        'few', 'got', 'him', 'how', 'man', 'may', 'not', 'oil',
        'one', 'our', 'own', 'run', 'sun', 'top', 'try', 'yet', 'yes',
        'day', 'end', 'way', 'any', 'may', 'say', 'new', 'old', 'see',
        'him', 'two', 'how', 'its', 'who', 'oil', 'sit', 'set', 'hot',
        'lot', 'cut', 'put', 'but', 'got', 'not', 'out', 'our', 'now',
        'low', 'few', 'new', 'too', 'you', 'use', 'run', 'sun', 'fun',
        'red', 'bed', 'led', 'fed', 'had', 'bad', 'mad', 'sad', 'dad',
        'add', 'all', 'call', 'ball', 'fall', 'wall', 'tall', 'small',
        'home', 'come', 'some', 'time', 'name', 'same', 'game', 'came',
        'take', 'make', 'wake', 'lake', 'cake', 'bake', 'sake', 'fake',
        'like', 'bike', 'hike', 'mike', 'pike', 'life', 'wife', 'nice',
        'rice', 'mice', 'dice', 'ice', 'face', 'race', 'pace', 'lace',
        'place', 'space', 'grace', 'trace', 'brace', 'fire', 'tire',
        'wire', 'hire', 'dire', 'mire', 'sure', 'pure', 'cure', 'lure',
        'blue', 'true', 'clue', 'glue', 'due', 'sue', 'hue', 'cue',
        'side', 'ride', 'hide', 'wide', 'tide', 'bride', 'pride', 'slide',
        'house', 'mouse', 'about', 'water', 'after', 'first', 'never',
        'other', 'right', 'think', 'where', 'being', 'every', 'great',
        'might', 'still', 'small', 'found', 'those', 'never', 'under',
        'while', 'again', 'place', 'right', 'three', 'state', 'after',
        'good', 'well', 'much', 'very', 'when', 'here', 'work', 'year',
        'back', 'down', 'over', 'also', 'just', 'only', 'know', 'take',
        'look', 'give', 'most', 'hand', 'high', 'part', 'head', 'keep',
        'help', 'turn', 'move', 'live', 'seem', 'feel', 'want', 'need',
        'find', 'tell', 'such', 'long', 'next', 'last', 'left', 'each',
        'both', 'many', 'more', 'than', 'same', 'them', 'what', 'does'
    }
    
    # Check if it's in our common words list
    if word in common_words:
        return True
    
    # Common word patterns for slightly longer words
    if len(word) <= 6:
        # Common suffixes
        common_endings = ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion', 'ness', 'ment', 'able']
        if any(word.endswith(ending) for ending in common_endings):
            return True
        
        # Common prefixes  
        common_starts = ['un', 're', 'pre', 'dis', 'mis', 'over', 'under', 'out']
        if any(word.startswith(start) for start in common_starts):
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
    global large_common_words
    is_large_common = word in large_common_words

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

    # Food dishes get highest priority for populated areas
    if is_food:
        score += 60  # Highest bonus
    # Large common words get second highest priority
    if is_large_common:
        score += 55
    # Common word bonus (legacy small set)
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
    global large_common_words
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

def load_common_words(filepath: str) -> set:
    """Load a large set of common English words from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip() and not line.startswith('#'))
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, skipping large common word bonus.")
        return set()

def main():
    print("TwoWords API - Word List Optimizer")
    print("=" * 50)
    
    # Load current words
    word_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'word-data')
    expanded_words_path = os.path.join(word_data_dir, 'expanded_words.txt')
    expanded_words_zip_path = os.path.join(word_data_dir, 'expanded_words.zip')
    food_dishes_path = os.path.join(word_data_dir, 'food_dishes_final.txt')
    important_indices_path = os.path.join(word_data_dir, 'important_indices.txt')
    common_words_path = os.path.join(word_data_dir, 'common_words.txt')
    output_file = os.path.join(word_data_dir, 'optimized_words.txt')
    sorted_output_file = os.path.join(word_data_dir, 'optimized_words_sorted_by_score.txt')

    print(f"Loading words from {expanded_words_path}...")
    try:
        with open(expanded_words_path, 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{expanded_words_path} not found, trying zip file...")
        words = load_words_from_zip(expanded_words_zip_path)
    print(f"Loaded {len(words):,} words")

    print("Loading food dishes for priority placement...")
    try:
        with open(food_dishes_path, 'r', encoding='utf-8') as f:
            food_dishes = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {food_dishes_path} not found, skipping food priority")
        food_dishes = []
    print(f"Loaded {len(food_dishes)} food dishes")

    print("Loading important population indices...")
    important_indices = load_important_indices(important_indices_path)
    print(f"Loaded {len(important_indices)} important indices")

    print("Loading large common words set for scoring...")
    global large_common_words
    large_common_words = load_common_words(common_words_path)

    optimized_words = optimize_word_list(words, important_indices, food_dishes)
    save_optimized_words(optimized_words, output_file)
    print(f"Saved optimized word list to {output_file}")

    # Always create expanded_words.zip in the workspace root (parent of python/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    zip_path = os.path.join(root_dir, 'expanded_words.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(output_file, arcname='expanded_words.txt')
    print(f"Created {zip_path} containing expanded_words.txt")

    print("\nOptimization Results:")
    print(f"Total words in optimized list: {len(optimized_words):,}")

    print(f"\nFOOD DISHES at major population centres:")
    important_list = sorted(list(important_indices))[:15]
    food_set = set(food_dishes)
    for idx in important_list:
        if idx < len(optimized_words):
            word = optimized_words[idx]
            is_food = word in food_set
            status = "🍽️ FOOD" if is_food else "❌ NON-FOOD"
            print(f"  Index {idx:6d}: '{word}' {status}")

    important_words = [optimized_words[idx] for idx in important_indices if idx < len(optimized_words)]
    food_at_important = sum(1 for word in important_words if word in food_set)
    print(f"\nFood dishes at important indices: {food_at_important}/{len(important_words)} ({food_at_important/len(important_words)*100:.1f}%)")

    food_count = sum(1 for word in optimized_words[:1000] if word in food_set)
    print(f"Food dishes in top 1000 positions: {food_count}")

    lengths = [len(word) for word in optimized_words[:1000]]
    avg_length = sum(lengths) / len(lengths)
    print(f"\nWord quality (first 1000 words):")
    print(f"  Average length: {avg_length:.1f} characters")
    print(f"  Short words (≤4 chars): {sum(1 for l in lengths if l <= 4)}")
    print(f"  Medium words (5-7 chars): {sum(1 for l in lengths if 5 <= l <= 7)}")
    print(f"  Long words (8+ chars): {sum(1 for l in lengths if l >= 8)}")

    # Save a version of the list sorted by score (not alphabetically)
    valid_scored = [
        calculate_word_score(w, food_set)
        for w in optimized_words
        if is_valid_english_word(w)
    ]
    valid_scored.sort(key=lambda ws: ws.score, reverse=True)
    save_optimized_words([ws.word for ws in valid_scored], sorted_output_file)
    print(f"Saved score-sorted word list to {sorted_output_file}")

if __name__ == "__main__":
    main()
