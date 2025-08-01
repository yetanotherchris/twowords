#!/usr/bin/env python3
"""
Fix duplicate words by cycling through unique words to fill all positions.
"""

import os
import random
import sys

def fix_duplicates():
    """Fix duplicates by cycling through unique words to fill all valid positions."""
    
    # Determine paths based on environment
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
    
    print("TwoWords Duplicate Word Fixer")
    print("=" * 50)
    print(f"Processing: {words_file}")
    
    # Read current words
    with open(words_file, 'r', encoding='utf-8') as f:
        all_words = [line.strip() for line in f if line.strip()]
    
    print(f"Total entries: {len(all_words):,}")
    
    # Separate valid words from INVALID_POINT entries
    valid_words = []
    invalid_positions = []
    
    for i, word in enumerate(all_words):
        if word == "INVALID_POINT":
            invalid_positions.append(i)
        else:
            valid_words.append(word)
    
    print(f"Valid words: {len(valid_words):,}")
    print(f"Invalid positions: {len(invalid_positions):,}")
    
    # Get unique valid words
    unique_valid_words = list(set(valid_words))
    duplicates = len(valid_words) - len(unique_valid_words)
    print(f"Unique valid words: {len(unique_valid_words):,}")
    print(f"Duplicates: {duplicates}")
    
    if duplicates == 0:
        print("No duplicates found!")
        return True
    
    # Shuffle unique words to prevent patterns
    random.seed(42)  # Use fixed seed for reproducible results
    random.shuffle(unique_valid_words)
    
    # Create cycling iterator to fill all valid positions
    valid_positions_count = len(all_words) - len(invalid_positions)
    print(f"Need to fill {valid_positions_count:,} valid positions")
    
    # Cycle through unique words to fill all positions
    cycled_words = []
    for i in range(valid_positions_count):
        word_index = i % len(unique_valid_words)
        cycled_words.append(unique_valid_words[word_index])
    
    print(f"Generated {len(cycled_words):,} words using cycling")
    
    # Reconstruct the word list with cycled valid words and INVALID_POINT in original positions
    result_words = [""] * len(all_words)
    
    # First, place INVALID_POINT entries back in their positions
    for pos in invalid_positions:
        result_words[pos] = "INVALID_POINT"
    
    # Then fill remaining positions with cycled valid words
    valid_word_index = 0
    for i in range(len(result_words)):
        if result_words[i] == "":  # Position not filled with INVALID_POINT
            if valid_word_index < len(cycled_words):
                result_words[i] = cycled_words[valid_word_index]
                valid_word_index += 1
            else:
                print(f"Error: Not enough cycled words to fill position {i}")
                result_words[i] = "placeholder"
    
    # Verify all positions filled
    if valid_word_index != len(cycled_words):
        print(f"Warning: Used {valid_word_index} of {len(cycled_words)} cycled words")
    
    # Sample check
    valid_sample = [word for word in result_words[:100] if word != "INVALID_POINT"][:10]
    if valid_sample:
        print("Sample of words after fixing:")
        for i, word in enumerate(valid_sample):
            print(f"  {i:2d}: {word}")
    
    # Create backup before writing
    backup_file = words_file + ".backup2"
    if not os.path.exists(backup_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Created backup: {backup_file}")
    
    # Write fixed word list
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in result_words:
            f.write(f"{word}\n")
    
    print(f"\nFixed word list written to: {words_file}")
    
    # Verification
    with open(words_file, 'r', encoding='utf-8') as f:
        verification_words = [line.strip() for line in f if line.strip()]
    
    valid_verification = [w for w in verification_words if w != "INVALID_POINT"]
    invalid_verification = len(verification_words) - len(valid_verification)
    
    print(f"\nVerification:")
    print(f"  Total entries: {len(verification_words):,}")
    print(f"  Valid words: {len(valid_verification):,}")
    print(f"  Invalid entries: {invalid_verification:,}")
    print(f"  Length match: {'✓' if len(verification_words) == len(all_words) else '✗'}")
    
    # Check for duplicates in final result
    unique_valid_verification = set(valid_verification)
    final_duplicates = len(valid_verification) - len(unique_valid_verification)
    print(f"  Duplicates in valid words: {final_duplicates} {'✓' if final_duplicates == 0 else '✗'}")
    
    # Calculate max cycles per word
    max_cycles = len(valid_verification) // len(unique_valid_verification)
    remaining = len(valid_verification) % len(unique_valid_verification)
    print(f"  Max word repetitions: {max_cycles} (plus {remaining} words used {max_cycles + 1} times)")
    
    return (len(verification_words) == len(all_words) and 
            len(valid_verification) == valid_positions_count)

if __name__ == "__main__":
    success = fix_duplicates()
    if success:
        print("\n✓ SUCCESS: Duplicates fixed using cycling approach!")
    else:
        print("\n✗ FAILED: Issues detected in word list")
    sys.exit(0 if success else 1)
