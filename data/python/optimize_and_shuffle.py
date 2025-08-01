#!/usr/bin/env python3
"""
Optimize and shuffle word list for better user experience.
- Prioritize 4-7 character words for better memorability
- Randomize word order to prevent similar words getting similar coordinates
- Ensure no alphabetical clustering that could cause confusion
"""

import os
import random
import sys

def optimize_word_list():
    """Optimize word list by prioritizing 4-7 char words and shuffling order."""
    
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    words_file = os.path.join(repo_root, "data", "output", "words.txt")
    
    if not os.path.exists(words_file):
        print(f"Error: {words_file} not found!")
        return False
    
    print("TwoWords Word List Optimizer")
    print("=" * 50)
    print(f"Processing: {words_file}")
    
    # Read current words
    with open(words_file, 'r', encoding='utf-8') as f:
        all_words = [line.strip() for line in f if line.strip()]
    
    print(f"Current word count: {len(all_words):,}")
    
    # Categorize words by length
    words_by_length = {}
    for word in all_words:
        length = len(word)
        if length not in words_by_length:
            words_by_length[length] = []
        words_by_length[length].append(word)
    
    # Show current distribution
    print("\nCurrent word length distribution:")
    for length in sorted(words_by_length.keys()):
        count = len(words_by_length[length])
        print(f"  {length} chars: {count:,} words")
    
    # Prioritize 4-7 character words
    target_count = 110001
    priority_words = []
    
    # First, add all 4-7 character words
    for length in [4, 5, 6, 7]:
        if length in words_by_length:
            priority_words.extend(words_by_length[length])
    
    print(f"\n4-7 character words: {len(priority_words):,}")
    
    # If we don't have enough 4-7 char words, add others in order of preference
    remaining_needed = target_count - len(priority_words)
    other_words = []
    
    if remaining_needed > 0:
        print(f"Need {remaining_needed:,} more words")
        
        # Add in order of preference: 3, 8, 2, 9, 10, 11, etc.
        preferred_lengths = [3, 8, 2, 9, 10, 11, 12, 1]
        
        for length in preferred_lengths:
            if length in words_by_length and remaining_needed > 0:
                available = words_by_length[length]
                to_add = min(len(available), remaining_needed)
                other_words.extend(available[:to_add])
                remaining_needed -= to_add
                print(f"  Added {to_add:,} words of length {length}")
                
                if remaining_needed <= 0:
                    break
    
    # Combine all selected words
    selected_words = priority_words + other_words
    
    # Trim to exact target if we have too many
    if len(selected_words) > target_count:
        selected_words = selected_words[:target_count]
    
    print(f"\nSelected words: {len(selected_words):,}")
    
    # Show final distribution
    final_distribution = {}
    for word in selected_words:
        length = len(word)
        final_distribution[length] = final_distribution.get(length, 0) + 1
    
    print("\nFinal word length distribution:")
    for length in sorted(final_distribution.keys()):
        count = final_distribution[length]
        percentage = (count / len(selected_words)) * 100
        print(f"  {length} chars: {count:,} words ({percentage:.1f}%)")
    
    # IMPORTANT: Shuffle the words to prevent alphabetical clustering
    print("\nShuffling words to prevent clustering...")
    random.seed(42)  # Use fixed seed for reproducible results
    random.shuffle(selected_words)
    
    # Verify shuffling worked by checking if similar words are separated
    print("Checking word distribution (first 20 words):")
    for i, word in enumerate(selected_words[:20]):
        print(f"  {i:5d}: {word}")
    
    # Additional check: ensure no alphabetical runs
    consecutive_alphabetical = 0
    max_consecutive = 0
    
    for i in range(1, min(1000, len(selected_words))):  # Check first 1000
        if selected_words[i] > selected_words[i-1]:
            consecutive_alphabetical += 1
            max_consecutive = max(max_consecutive, consecutive_alphabetical)
        else:
            consecutive_alphabetical = 0
    
    print(f"Max consecutive alphabetical words in first 1000: {max_consecutive}")
    
    # Create backup before writing
    backup_file = words_file + ".backup"
    if not os.path.exists(backup_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Created backup: {backup_file}")
    
    # Write optimized and shuffled word list
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in selected_words:
            f.write(f"{word}\n")
    
    print(f"\nOptimized word list written to: {words_file}")
    
    # Verification
    with open(words_file, 'r', encoding='utf-8') as f:
        verification_words = [line.strip() for line in f if line.strip()]
    
    print(f"\nVerification:")
    print(f"  Total words: {len(verification_words):,}")
    print(f"  Target words: {target_count:,}")
    print(f"  Match: {'✓' if len(verification_words) == target_count else '✗'}")
    
    # Check for duplicates
    unique_words = set(verification_words)
    duplicates = len(verification_words) - len(unique_words)
    print(f"  Duplicates: {duplicates} {'✓' if duplicates == 0 else '✗'}")
    
    # Check specific test words are still present
    test_words = ['tree', 'trousers', 'big', 'small', 'home']
    found_test_words = [word for word in test_words if word in unique_words]
    print(f"  Test words found: {found_test_words}")
    
    # Show sample of words to verify good distribution
    print(f"\nSample words from different positions:")
    sample_positions = [0, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
    for pos in sample_positions:
        if pos < len(verification_words):
            word = verification_words[pos]
            print(f"  Position {pos:6d}: {word} ({len(word)} chars)")
    
    return len(verification_words) == target_count and duplicates == 0

if __name__ == "__main__":
    success = optimize_word_list()
    if success:
        print("\n✓ SUCCESS: Word list optimized and shuffled!")
    else:
        print("\n✗ FAILED: Issues detected in word list")
    sys.exit(0 if success else 1)
