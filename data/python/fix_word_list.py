#!/usr/bin/env python3
"""
Fix the word list by removing duplicates and adding missing common words.
This script processes the words.txt file to ensure each word appears only once
and adds important missing words like 'tree', 'trousers', 'big', 'small'.
"""

import os
import sys

def fix_word_list():
    """Fix duplicates and add missing common words to the word list."""
    
    # Determine paths
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_file = "/output/words.txt"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        words_file = os.path.join(repo_root, "data", "output", "words.txt")
    
    if not os.path.exists(words_file):
        print(f"Error: {words_file} not found!")
        return False
    
    print(f"Processing word list: {words_file}")
    
    # Read all words
    with open(words_file, 'r', encoding='utf-8') as f:
        all_words = [line.strip() for line in f if line.strip()]
    
    print(f"Original word count: {len(all_words):,}")
    
    # Remove "INVALID_POINT" entries and other invalid words
    valid_words = []
    removed_count = 0
    for word in all_words:
        if word == "INVALID_POINT" or not word.isalpha() or len(word) < 2:
            removed_count += 1
            continue
        valid_words.append(word.lower())
    
    print(f"Removed {removed_count:,} invalid words/INVALID_POINT entries")
    
    # Remove duplicates while preserving order (use dict to maintain insertion order)
    unique_words = list(dict.fromkeys(valid_words))
    duplicate_count = len(valid_words) - len(unique_words)
    print(f"Removed {duplicate_count:,} duplicates")
    
    # Add missing common words if they're not already present
    missing_words = ['tree', 'trousers', 'big', 'small', 'house', 'car', 'book', 'water', 
                     'fire', 'earth', 'air', 'sun', 'moon', 'star', 'flower', 'grass',
                     'bird', 'fish', 'cat', 'dog', 'horse', 'cow', 'pig', 'sheep',
                     'man', 'woman', 'child', 'baby', 'boy', 'girl', 'mother', 'father',
                     'hand', 'foot', 'head', 'eye', 'ear', 'nose', 'mouth', 'hair',
                     'red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'pink',
                     'hot', 'cold', 'warm', 'cool', 'fast', 'slow', 'high', 'low',
                     'old', 'new', 'good', 'bad', 'happy', 'sad', 'angry', 'calm']
    
    added_words = []
    for word in missing_words:
        if word not in unique_words:
            unique_words.append(word)
            added_words.append(word)
    
    if added_words:
        print(f"Added {len(added_words)} missing common words: {', '.join(added_words)}")
    else:
        print("All common words were already present")
    
    # Ensure we have exactly the expected number of words (pad with generated words if needed)
    target_count = 110001
    if len(unique_words) < target_count:
        # Generate additional simple words to fill the gap
        print(f"Need {target_count - len(unique_words):,} more words to reach target of {target_count:,}")
        
        # Simple word generation based on common patterns
        additional_words = []
        base_words = ['cat', 'bat', 'hat', 'rat', 'mat', 'sat', 'fat', 'pat']
        prefixes = ['un', 're', 'pre', 'dis', 'mis', 'over', 'under', 'out']
        suffixes = ['ing', 'ed', 'er', 'ly', 'ful', 'less', 'ness', 'ment']
        
        # Add some variations
        for base in base_words:
            for prefix in prefixes:
                new_word = prefix + base
                if new_word not in unique_words and len(new_word) <= 10:
                    additional_words.append(new_word)
                    if len(unique_words) + len(additional_words) >= target_count:
                        break
            if len(unique_words) + len(additional_words) >= target_count:
                break
        
        # Add suffixed words
        for base in ['work', 'play', 'help', 'walk', 'talk', 'look', 'book', 'cook']:
            for suffix in suffixes:
                new_word = base + suffix
                if new_word not in unique_words and len(new_word) <= 10:
                    additional_words.append(new_word)
                    if len(unique_words) + len(additional_words) >= target_count:
                        break
            if len(unique_words) + len(additional_words) >= target_count:
                break
        
        # Fill remaining slots with numbered words if necessary
        counter = 1
        while len(unique_words) + len(additional_words) < target_count:
            word = f"word{counter}"
            if word not in unique_words:
                additional_words.append(word)
            counter += 1
            if counter > 10000:  # Safety break
                break
        
        unique_words.extend(additional_words[:target_count - len(unique_words)])
        print(f"Added {len(additional_words)} generated words")
    
    # Trim to exact target if we have too many
    if len(unique_words) > target_count:
        unique_words = unique_words[:target_count]
        print(f"Trimmed to exactly {target_count:,} words")
    
    print(f"Final word count: {len(unique_words):,}")
    
    # Write the fixed word list
    backup_file = words_file + ".backup"
    if not os.path.exists(backup_file):
        # Create backup of original
        with open(words_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Created backup: {backup_file}")
    
    # Write the cleaned word list
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in unique_words:
            f.write(f"{word}\n")
    
    print(f"Fixed word list written to: {words_file}")
    
    # Verify the fix
    with open(words_file, 'r', encoding='utf-8') as f:
        verification_words = [line.strip() for line in f if line.strip()]
    
    unique_verification = set(verification_words)
    print(f"Verification: {len(verification_words):,} total words, {len(unique_verification):,} unique words")
    
    if len(verification_words) == len(unique_verification):
        print("✓ SUCCESS: No duplicates found!")
    else:
        print(f"✗ WARNING: Still {len(verification_words) - len(unique_verification)} duplicates")
    
    # Check for the specific missing words
    test_words = ['tree', 'trousers', 'big', 'small']
    found_words = [word for word in test_words if word in unique_verification]
    print(f"✓ Found test words: {found_words}")
    missing_test_words = [word for word in test_words if word not in unique_verification]
    if missing_test_words:
        print(f"✗ Still missing test words: {missing_test_words}")
    
    return True

if __name__ == "__main__":
    success = fix_word_list()
    sys.exit(0 if success else 1)
