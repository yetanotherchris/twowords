#!/usr/bin/env python3
"""
Add missing essential words to the word list.
"""

import os

def add_missing_words():
    """Add the specific missing words that were requested."""
    
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    words_file = os.path.join(repo_root, "data", "output", "words.txt")
    
    # Read current words
    with open(words_file, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    print(f"Current word count: {len(words):,}")
    
    # Check which words are missing
    missing_words = ['tree', 'trousers', 'small']
    words_set = set(words)
    
    actually_missing = []
    for word in missing_words:
        if word not in words_set:
            actually_missing.append(word)
            print(f"Missing: {word}")
        else:
            print(f"Found: {word}")
    
    if actually_missing:
        # Add missing words at the beginning (they'll get better indices)
        new_words = actually_missing + words
        
        # Trim to maintain exact count
        if len(new_words) > len(words):
            new_words = new_words[:len(words)]
        
        # Write back
        with open(words_file, 'w', encoding='utf-8') as f:
            for word in new_words:
                f.write(f"{word}\n")
        
        print(f"Added {len(actually_missing)} missing words: {actually_missing}")
        print(f"Final word count: {len(new_words):,}")
    else:
        print("All requested words are already present!")
    
    # Final verification
    with open(words_file, 'r', encoding='utf-8') as f:
        final_words = [line.strip() for line in f if line.strip()]
    
    final_set = set(final_words)
    test_words = ['tree', 'trousers', 'big', 'small', 'home']
    
    print("\nFinal verification:")
    for word in test_words:
        status = "✓" if word in final_set else "✗"
        print(f"  {status} {word}")

if __name__ == "__main__":
    add_missing_words()
