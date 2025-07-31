#!/usr/bin/env python3
"""
Simple fix: Create a word list where valid UK coordinate indices get real words.
"""

import zipfile
import math

# Constants from the API
WORDS_NEEDED = 110001
LAT_MIN, LAT_MAX = 49.0, 60.0
LON_MIN, LON_MAX = -8.0, 2.0
STEP = 0.0001

def is_valid_uk_land(lat: float, lon: float) -> bool:
    """Simple UK land validation."""
    # Basic UK bounding box with water exclusions
    if lat < 50.0 or lat > 59.0 or lon < -6.0 or lon > 2.0:
        return False
    
    # Exclude major water bodies (simplified)
    # Celtic Sea / Atlantic exclusions
    if lat < 52.0 and lon < -4.0:
        return False
    
    # North Sea exclusions  
    if lat > 55.0 and lon > 0.0:
        return False
    
    # More detailed water exclusions
    exclusions = [
        # Celtic Sea area (where "loud.fart" was pointing)
        (lat >= 50.5 and lat <= 51.5 and lon >= -6.0 and lon <= -4.5),
        # Bristol Channel
        (lat >= 51.0 and lat <= 51.5 and lon >= -4.5 and lon <= -2.5),
        # Thames Estuary outer
        (lat >= 51.2 and lat <= 51.6 and lon >= 0.5 and lon <= 1.5),
        # The Wash
        (lat >= 52.7 and lat <= 53.1 and lon >= 0.0 and lon <= 0.8),
    ]
    
    if any(exclusions):
        return False
    
    return True

def load_word_list():
    """Load a simple word list."""
    words = []
    
    # Try to load from Norvig list
    try:
        with open('../word-data/norvig-word-list.txt', 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if 3 <= len(word) <= 8 and word.isalpha():
                    words.append(word)
    except FileNotFoundError:
        # Fallback word list
        words = [
            'apple', 'beach', 'chair', 'dance', 'earth', 'flame', 'green', 'house', 'input', 'jolly',
            'knife', 'lemon', 'mouse', 'north', 'ocean', 'plant', 'queen', 'river', 'snake', 'table',
            'under', 'voice', 'water', 'zebra', 'bread', 'cloud', 'dream', 'field', 'glass', 'happy'
        ]
    
    return words[:15000]  # Limit to first 15k words

def create_simple_word_list():
    """Create a simple word list that ensures London works."""
    words = load_word_list()
    print(f"Loaded {len(words)} words")

    word_list = ["INVALID"] * WORDS_NEEDED
    word_idx = 0

    for i in range(WORDS_NEEDED):
        # Compute lat/lon for this index (lat for i, lon for i)
        lat = LAT_MIN + i * STEP
        lon = LON_MIN + i * STEP

        # Assign word to valid land cells only
        if is_valid_uk_land(lat, lon):
            if word_idx < len(words):
                word_list[i] = words[word_idx]
                word_idx += 1
            else:
                # If we run out of words, cycle (should not happen with correct list)
                word_list[i] = words[word_idx % len(words)]
                word_idx += 1
        # else: leave as 'INVALID'

    print(f"Assigned {word_idx} words to valid UK land indices.")
    valid_count = sum(1 for w in word_list if w != "INVALID")
    print(f"Final result: {valid_count:,} valid words, {WORDS_NEEDED - valid_count:,} invalid positions")
    return word_list

def save_word_list(words):
    """Save the word list."""
    with zipfile.ZipFile('../expanded_words.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('expanded_words.txt', '\n'.join(words))
    print("Saved to ../expanded_words.zip")

if __name__ == "__main__":
    print("Creating simple fixed word list...")
    word_list = create_simple_word_list()
    save_word_list(word_list)
    print("Done!")
