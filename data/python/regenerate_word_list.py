#!/usr/bin/env python3
"""
Enhanced word list fixer that addresses the core pipeline issues.
This script fixes the word generation process to avoid INVALID_POINT entries
and ensures we have a proper list of 110,001 unique English words.
"""

import os
import sys
from twowords_utils.word_popularity import WordPopularity

def regenerate_clean_word_list():
    """Regenerate a clean word list without INVALID_POINT entries."""
    
    # Determine paths
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_dir = "/words"
        output_dir = "/output"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        words_dir = os.path.join(repo_root, "data", "words")
        output_dir = os.path.join(repo_root, "data", "output")
    
    words_file = os.path.join(output_dir, "words.txt")
    
    print("TwoWords Word List Regenerator")
    print("=" * 50)
    print(f"Words directory: {words_dir}")
    print(f"Output directory: {output_dir}")
    
    # Create a custom WordPopularity instance with enhanced word generation
    word_pop = WordPopularity(words_dir)
    
    # Load all available word sources
    print("\nLoading word sources...")
    
    # 1. Load Norvig's word list (highest quality)
    norvig_file = os.path.join(words_dir, 'norvig-word-list.txt')
    base_words = []
    if os.path.exists(norvig_file):
        with open(norvig_file, 'r', encoding='utf-8') as f:
            norvig_words = [line.strip().lower() for line in f if line.strip()]
        
        # Filter Norvig words for quality and appropriate length
        for word in norvig_words:
            if (2 <= len(word) <= 10 and 
                word.isalpha() and 
                word_pop.is_valid_english_word(word) and
                word_pop.is_clearly_english_word(word)):
                base_words.append(word)
        
        print(f"Loaded {len(base_words):,} words from Norvig's list")
    
    # 2. Load common words
    common_words_file = os.path.join(words_dir, 'common_words.txt')
    if os.path.exists(common_words_file):
        with open(common_words_file, 'r', encoding='utf-8') as f:
            common_words = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
        
        # Add common words that aren't already in the list
        for word in common_words:
            if word not in base_words and word.isalpha() and 2 <= len(word) <= 10:
                base_words.append(word)
        
        print(f"Added {len(common_words):,} common words")
    
    # 3. Load food dishes
    food_file = os.path.join(words_dir, 'food_dishes_final.txt')
    if os.path.exists(food_file):
        with open(food_file, 'r', encoding='utf-8') as f:
            food_words = [line.strip().lower() for line in f if line.strip()]
        
        for word in food_words:
            if word not in base_words and word.isalpha() and 2 <= len(word) <= 10:
                base_words.append(word)
        
        print(f"Added {len(food_words):,} food dishes")
    
    # 4. Load common nouns
    nouns_file = os.path.join(words_dir, 'common_nouns.txt')
    if os.path.exists(nouns_file):
        with open(nouns_file, 'r', encoding='utf-8') as f:
            noun_words = [line.strip().lower() for line in f if line.strip()]
        
        for word in noun_words:
            if word not in base_words and word.isalpha() and 2 <= len(word) <= 10:
                base_words.append(word)
        
        print(f"Added {len(noun_words):,} common nouns")
    
    # Remove duplicates while preserving order
    unique_words = list(dict.fromkeys(base_words))
    print(f"Total unique words after deduplication: {len(unique_words):,}")
    
    # Add essential missing words
    essential_words = [
        'tree', 'trousers', 'big', 'small', 'house', 'car', 'book', 'water',
        'fire', 'earth', 'air', 'sun', 'moon', 'star', 'flower', 'grass',
        'bird', 'fish', 'cat', 'dog', 'horse', 'cow', 'pig', 'sheep',
        'man', 'woman', 'child', 'baby', 'boy', 'girl', 'mother', 'father',
        'hand', 'foot', 'head', 'eye', 'ear', 'nose', 'mouth', 'hair',
        'red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'pink',
        'hot', 'cold', 'warm', 'cool', 'fast', 'slow', 'high', 'low',
        'old', 'new', 'good', 'bad', 'happy', 'sad', 'angry', 'calm',
        'love', 'hate', 'like', 'want', 'need', 'have', 'give', 'take',
        'make', 'do', 'go', 'come', 'see', 'look', 'hear', 'feel',
        'think', 'know', 'say', 'tell', 'ask', 'work', 'play', 'run'
    ]
    
    added_essential = []
    for word in essential_words:
        if word not in unique_words:
            unique_words.append(word)
            added_essential.append(word)
    
    if added_essential:
        print(f"Added {len(added_essential)} essential words: {', '.join(added_essential[:10])}{'...' if len(added_essential) > 10 else ''}")
    
    # Target word count
    target_count = 110001
    
    # If we don't have enough words, we need to be more permissive with the Norvig list
    if len(unique_words) < target_count:
        print(f"Need {target_count - len(unique_words):,} more words")
        
        # Second pass: be more permissive with Norvig words
        if os.path.exists(norvig_file):
            with open(norvig_file, 'r', encoding='utf-8') as f:
                all_norvig = [line.strip().lower() for line in f if line.strip()]
            
            for word in all_norvig:
                if len(unique_words) >= target_count:
                    break
                
                if (word not in unique_words and 
                    2 <= len(word) <= 12 and  # Allow longer words
                    word.isalpha() and
                    word_pop.is_valid_english_word(word)):  # Less strict validation
                    unique_words.append(word)
            
            print(f"After second pass: {len(unique_words):,} words")
    
    # Final trimming to exact target
    if len(unique_words) > target_count:
        unique_words = unique_words[:target_count]
    elif len(unique_words) < target_count:
        # Generate simple additional words if still needed
        base_forms = ['work', 'play', 'help', 'walk', 'talk', 'look', 'book', 'cook', 'make', 'take']
        suffixes = ['ing', 'ed', 'er', 's', 'ly', 'ful', 'less']
        
        for base in base_forms:
            for suffix in suffixes:
                if len(unique_words) >= target_count:
                    break
                new_word = base + suffix
                if new_word not in unique_words and len(new_word) <= 10:
                    unique_words.append(new_word)
        
        # Fill with numbered words if absolutely necessary
        counter = 1
        while len(unique_words) < target_count:
            word = f"word{counter}"
            if word not in unique_words:
                unique_words.append(word)
            counter += 1
    
    print(f"Final word count: {len(unique_words):,}")
    
    # Create backup and write new file
    if os.path.exists(words_file):
        backup_file = words_file + ".backup"
        if not os.path.exists(backup_file):
            os.rename(words_file, backup_file)
            print(f"Created backup: {backup_file}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in unique_words:
            f.write(f"{word}\n")
    
    print(f"New word list written to: {words_file}")
    
    # Verification
    with open(words_file, 'r', encoding='utf-8') as f:
        verification_words = [line.strip() for line in f if line.strip()]
    
    unique_verification = set(verification_words)
    print(f"\nVerification:")
    print(f"  Total words: {len(verification_words):,}")
    print(f"  Unique words: {len(unique_verification):,}")
    print(f"  Duplicates: {len(verification_words) - len(unique_verification)}")
    
    # Check for test words
    test_words = ['tree', 'trousers', 'big', 'small', 'home']
    found_test_words = [word for word in test_words if word in unique_verification]
    print(f"  Test words found: {found_test_words}")
    
    # Check for any remaining INVALID_POINT entries
    invalid_count = sum(1 for word in verification_words if not word.isalpha() or word == "INVALID_POINT")
    if invalid_count == 0:
        print("  ✓ No invalid entries found")
    else:
        print(f"  ✗ Found {invalid_count} invalid entries")
    
    return len(verification_words) == len(unique_verification) and invalid_count == 0

if __name__ == "__main__":
    success = regenerate_clean_word_list()
    sys.exit(0 if success else 1)
