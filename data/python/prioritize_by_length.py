#!/usr/bin/env python3
"""
Properly prioritize 4-7 character words by placing them first in the list.
- Place all 4-7 character words at the beginning (shuffled within this group)
- Place remaining words after (shuffled within their group)  
- This ensures 4-7 char words get the best coordinates while preventing clustering
"""

import os
import random
import sys

def properly_prioritize_words():
    """Place 4-7 char words first, then others, with shuffling within each group."""
    
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    words_file = os.path.join(repo_root, "data", "output", "words.txt")
    
    if not os.path.exists(words_file):
        print(f"Error: {words_file} not found!")
        return False
    
    print("TwoWords Word List Priority Optimizer")
    print("=" * 50)
    print(f"Processing: {words_file}")
    
    # Read current words
    with open(words_file, 'r', encoding='utf-8') as f:
        all_words = [line.strip() for line in f if line.strip()]
    
    print(f"Current word count: {len(all_words):,}")
    
    # Separate words by priority
    priority_words = []  # 4-7 characters
    other_words = []     # All other lengths
    
    for word in all_words:
        if 4 <= len(word) <= 7:
            priority_words.append(word)
        else:
            other_words.append(word)
    
    print(f"\n4-7 character words: {len(priority_words):,}")
    print(f"Other length words: {len(other_words):,}")
    
    # Show length distribution of priority words
    priority_distribution = {}
    for word in priority_words:
        length = len(word)
        priority_distribution[length] = priority_distribution.get(length, 0) + 1
    
    print("\nPriority words (4-7 chars) distribution:")
    for length in sorted(priority_distribution.keys()):
        count = priority_distribution[length]
        percentage = (count / len(priority_words)) * 100
        print(f"  {length} chars: {count:,} words ({percentage:.1f}%)")
    
    # Shuffle within each group to prevent clustering
    print("\nShuffling within priority groups...")
    random.seed(42)  # Fixed seed for reproducibility
    random.shuffle(priority_words)
    random.shuffle(other_words)
    
    # Combine: priority words first, then others
    final_words = priority_words + other_words
    
    print(f"\nFinal arrangement:")
    print(f"  Positions 0-{len(priority_words)-1:,}: 4-7 character words")
    print(f"  Positions {len(priority_words):,}-{len(final_words)-1:,}: Other length words")
    
    # Verify no clustering by checking samples
    print(f"\nFirst 20 words (should all be 4-7 chars):")
    for i in range(min(20, len(final_words))):
        word = final_words[i]
        print(f"  {i:2d}: {word} ({len(word)} chars)")
    
    print(f"\nWords around position {len(priority_words)} (transition point):")
    transition = len(priority_words)
    start = max(0, transition - 5)
    end = min(len(final_words), transition + 5)
    for i in range(start, end):
        word = final_words[i]
        marker = " <-- TRANSITION" if i == transition else ""
        print(f"  {i:6d}: {word} ({len(word)} chars){marker}")
    
    # Check for alphabetical clustering in first 1000 words
    consecutive_alphabetical = 0
    max_consecutive = 0
    
    for i in range(1, min(1000, len(final_words))):
        if final_words[i] > final_words[i-1]:
            consecutive_alphabetical += 1
            max_consecutive = max(max_consecutive, consecutive_alphabetical)
        else:
            consecutive_alphabetical = 0
    
    print(f"\nMax consecutive alphabetical words in first 1000: {max_consecutive}")
    
    # Create backup before writing
    backup_file = words_file + ".backup2"
    if not os.path.exists(backup_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Created backup: {backup_file}")
    
    # Write prioritized word list
    with open(words_file, 'w', encoding='utf-8') as f:
        for word in final_words:
            f.write(f"{word}\n")
    
    print(f"\nPrioritized word list written to: {words_file}")
    
    # Verification
    with open(words_file, 'r', encoding='utf-8') as f:
        verification_words = [line.strip() for line in f if line.strip()]
    
    print(f"\nVerification:")
    print(f"  Total words: {len(verification_words):,}")
    print(f"  Expected: {len(final_words):,}")
    print(f"  Match: {'✓' if len(verification_words) == len(final_words) else '✗'}")
    
    # Check first 100 words are all 4-7 chars
    first_100_priority = all(4 <= len(word) <= 7 for word in verification_words[:100])
    print(f"  First 100 words are 4-7 chars: {'✓' if first_100_priority else '✗'}")
    
    # Check for duplicates
    unique_words = set(verification_words)
    duplicates = len(verification_words) - len(unique_words)
    print(f"  Duplicates: {duplicates} {'✓' if duplicates == 0 else '✗'}")
    
    # Check specific test words are still present
    test_words = ['tree', 'trousers', 'big', 'small', 'home']
    found_test_words = [word for word in test_words if word in unique_words]
    print(f"  Test words found: {found_test_words}")
    
    # Show final statistics
    first_1000_lengths = [len(word) for word in verification_words[:1000]]
    priority_in_first_1000 = sum(1 for length in first_1000_lengths if 4 <= length <= 7)
    print(f"  4-7 char words in first 1000: {priority_in_first_1000}/1000 ({priority_in_first_1000/10:.1f}%)")
    
    return (len(verification_words) == len(final_words) and 
            duplicates == 0 and 
            first_100_priority)

if __name__ == "__main__":
    success = properly_prioritize_words()
    if success:
        print("\n✓ SUCCESS: Words properly prioritized by length!")
    else:
        print("\n✗ FAILED: Issues detected in prioritization")
    sys.exit(0 if success else 1)
