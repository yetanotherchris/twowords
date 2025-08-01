#!/usr/bin/env python3
"""
Shuffle words in the filtered word list while preserving INVALID_POINT entries.
This ensures words are randomly distributed but polygon filtering is maintained.
"""

import os
import random
import sys

def shuffle_filtered_words():
    """Shuffle only the valid words while keeping INVALID_POINT entries in place."""
    
    # Determine paths based on environment
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_file = "/output/words.txt"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        words_file = os.path.join(repo_root, "data", "output", "words.txt")
    
    if not os.path.exists(words_file):
        print(f"Error: {words_file} not found!")
        return False
    
    print("TwoWords Word List Shuffler")
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
    
    # Check for duplicates in valid words
    unique_valid_words = list(set(valid_words))
    duplicates = len(valid_words) - len(unique_valid_words)
    print(f"Duplicate valid words: {duplicates}")
    
    if duplicates > 0:
        print("Removing duplicates from valid words...")
        valid_words = unique_valid_words
        print(f"Valid words after deduplication: {len(valid_words):,}")
    
    # Shuffle the valid words to prevent alphabetical clustering
    print("Shuffling valid words...")
    random.seed(42)  # Use fixed seed for reproducible results
    random.shuffle(valid_words)
    
    # Reconstruct the word list with shuffled valid words and INVALID_POINT in original positions
    result_words = [""] * len(all_words)
    
    # First, place INVALID_POINT entries back in their positions
    for pos in invalid_positions:
        result_words[pos] = "INVALID_POINT"
    
    # Then fill remaining positions with shuffled valid words
    valid_word_index = 0
    for i in range(len(result_words)):
        if result_words[i] == "":  # Position not filled with INVALID_POINT
            if valid_word_index < len(valid_words):
                result_words[i] = valid_words[valid_word_index]
                valid_word_index += 1
            else:
                print(f"Warning: Not enough valid words to fill position {i}")
                result_words[i] = "placeholder"
    
    # If we have leftover valid words, something went wrong
    if valid_word_index < len(valid_words):
        print(f"Warning: {len(valid_words) - valid_word_index} valid words not placed")
    
    # Verify shuffling worked by checking if similar words are separated
    valid_sample = [word for word in result_words[:100] if word != "INVALID_POINT"][:20]
    if valid_sample:
        print("Sample of shuffled valid words (first 20 encountered):")
        for i, word in enumerate(valid_sample):
            print(f"  {i:2d}: {word}")
    
    # Additional check: ensure no alphabetical runs in valid words
    valid_words_only = [word for word in result_words if word != "INVALID_POINT"]
    consecutive_alphabetical = 0
    max_consecutive = 0
    
    for i in range(1, min(1000, len(valid_words_only))):  # Check first 1000 valid words
        if valid_words_only[i] > valid_words_only[i-1]:
            consecutive_alphabetical += 1
            max_consecutive = max(max_consecutive, consecutive_alphabetical)
        else:
            consecutive_alphabetical = 0
    
    print(f"Max consecutive alphabetical words in first 1000 valid words: {max_consecutive}")
    
    # Create backup before writing
    backup_file = words_file + ".backup"
    if not os.path.exists(backup_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Created backup: {backup_file}")
    
    # Write shuffled word list
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in result_words:
            f.write(f"{word}\n")
    
    print(f"\nShuffled word list written to: {words_file}")
    
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
    
    # Check specific test words are still present
    test_words = ['tree', 'home', 'apple', 'house', 'water']
    found_test_words = [word for word in test_words if word in unique_valid_verification]
    print(f"  Test words found: {found_test_words}")
    
    # Show sample of words from different positions to verify good distribution
    print(f"\nSample words from different positions:")
    sample_positions = [0, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
    for pos in sample_positions:
        if pos < len(verification_words):
            word = verification_words[pos]
            if word != "INVALID_POINT":
                print(f"  Position {pos:6d}: {word} ({len(word)} chars)")
            else:
                print(f"  Position {pos:6d}: INVALID_POINT")
    
    return (len(verification_words) == len(all_words) and 
            final_duplicates == 0 and 
            len(valid_verification) == len(valid_words))

if __name__ == "__main__":
    success = shuffle_filtered_words()
    if success:
        print("\n✓ SUCCESS: Word list shuffled while preserving polygon filtering!")
    else:
        print("\n✗ FAILED: Issues detected in word list")
    sys.exit(0 if success else 1)
