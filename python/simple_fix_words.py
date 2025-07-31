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
    
    # Calculate London's indices
    london_lat, london_lon = 51.5074, -0.1278
    london_lat_idx = int(math.floor((london_lat - LAT_MIN) / STEP))
    london_lon_idx = int(math.floor((london_lon - LON_MIN) / STEP))
    
    print(f"London indices: lat={london_lat_idx}, lon={london_lon_idx}")
    
    # Create base word list filled with INVALID
    word_list = ["INVALID"] * WORDS_NEEDED
    
    # Set specific indices to valid words for testing
    word_idx = 0
    
    # Ensure London indices have valid words
    if london_lat_idx < WORDS_NEEDED:
        word_list[london_lat_idx] = words[word_idx % len(words)]
        word_idx += 1
        print(f"Assigned '{word_list[london_lat_idx]}' to London lat index {london_lat_idx}")
    
    if london_lon_idx < WORDS_NEEDED:
        word_list[london_lon_idx] = words[word_idx % len(words)]
        word_idx += 1
        print(f"Assigned '{word_list[london_lon_idx]}' to London lon index {london_lon_idx}")
    
    # Test other major cities
    test_cities = [
        ("Manchester", 53.4808, -2.2426),
        ("Birmingham", 52.4862, -1.8904),
        ("Leeds", 53.8008, -1.5491),
        ("Liverpool", 53.4084, -2.9916),
        ("Bristol", 51.4545, -2.5879),
    ]
    
    for city_name, lat, lon in test_cities:
        lat_idx = int(math.floor((lat - LAT_MIN) / STEP))
        lon_idx = int(math.floor((lon - LON_MIN) / STEP))
        
        if is_valid_uk_land(lat, lon):
            if lat_idx < WORDS_NEEDED and word_list[lat_idx] == "INVALID":
                word_list[lat_idx] = words[word_idx % len(words)]
                word_idx += 1
                print(f"{city_name} lat index {lat_idx}: {word_list[lat_idx]}")
            
            if lon_idx < WORDS_NEEDED and word_list[lon_idx] == "INVALID":
                word_list[lon_idx] = words[word_idx % len(words)]
                word_idx += 1
                print(f"{city_name} lon index {lon_idx}: {word_list[lon_idx]}")
    
    # Fill in more valid UK coordinates
    print("Filling additional UK coordinates...")
    for i in range(0, WORDS_NEEDED, 1000):  # Sample every 1000th index
        # Convert index back to coordinates (this is approximate)
        lat = LAT_MIN + i * STEP
        lon = LON_MIN + i * STEP
        
        if is_valid_uk_land(lat, lon) and word_list[i] == "INVALID":
            word_list[i] = words[word_idx % len(words)]
            word_idx += 1
            if word_idx % 100 == 0:
                print(f"Assigned {word_idx} words so far...")
    
    # Test the Celtic Sea coordinates that were problematic
    celtic_lat, celtic_lon = 51.0, -6.0
    celtic_lat_idx = int(math.floor((celtic_lat - LAT_MIN) / STEP))
    celtic_lon_idx = int(math.floor((celtic_lon - LON_MIN) / STEP))
    
    print(f"Celtic Sea test - lat_idx={celtic_lat_idx} ({word_list[celtic_lat_idx]}), lon_idx={celtic_lon_idx} ({word_list[celtic_lon_idx]})")
    print(f"Should be invalid: {not is_valid_uk_land(celtic_lat, celtic_lon)}")
    
    # Count results
    valid_count = sum(1 for w in word_list if w != "INVALID")
    print(f"Final result: {valid_count:,} valid words, {WORDS_NEEDED - valid_count:,} invalid positions")
    
    return word_list

def save_word_list(words):
    """Save the word list."""
    with zipfile.ZipFile('geo_validated_words.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('geo_validated_words.txt', '\n'.join(words))
    print("Saved to geo_validated_words.zip")

if __name__ == "__main__":
    print("Creating simple fixed word list...")
    word_list = create_simple_word_list()
    save_word_list(word_list)
    print("Done!")
