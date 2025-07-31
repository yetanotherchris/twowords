#!/usr/bin/env python3
"""
Fix the geographic word list to properly handle separate lat/lon indexing.
"""

import zipfile
import re
from typing import List, Set, Dict
from dataclasses import dataclass

# Constants from the API
WORDS_NEEDED = 110001
LAT_MIN, LAT_MAX = 49.0, 60.0
LON_MIN, LON_MAX = -8.0, 2.0
STEP = 0.0001

INVALID_MARKER = "INVALID"

def is_valid_uk_land(lat: float, lon: float) -> bool:
    """Enhanced UK land validation using more precise geographic rules."""
    
    # Core UK population rectangle (covers ~80% of UK population)
    core_uk = {
        'lat_min': 50.7,  # Brighton/South coast
        'lat_max': 54.0,  # Just north of Manchester/Leeds  
        'lon_min': -4.5,  # West Wales/Cornwall
        'lon_max': 1.8    # East coast Essex/Kent
    }
    
    # Check if in core populated area
    in_core = (lat >= core_uk['lat_min'] and lat <= core_uk['lat_max'] and 
               lon >= core_uk['lon_min'] and lon <= core_uk['lon_max'])
    
    if in_core:
        # Within core area, exclude major water bodies and mountains
        exclusions = [
            # Bristol Channel and Severn Estuary
            (lat >= 51.3 and lat <= 51.7 and lon >= -4.5 and lon <= -2.5),
            # The Wash (East England)
            (lat >= 52.7 and lat <= 53.1 and lon >= 0.0 and lon <= 0.8),
            # Thames Estuary (outer areas)
            (lat >= 51.3 and lat <= 51.6 and lon >= 0.5 and lon <= 1.8),
            # Exmoor/Dartmoor (Southwest highlands)
            (lat >= 50.7 and lat <= 51.3 and lon >= -4.5 and lon <= -3.3),
            # Peak District core (mountainous)
            (lat >= 53.1 and lat <= 53.5 and lon >= -2.0 and lon <= -1.5),
            # North Wales mountains (Snowdonia)
            (lat >= 52.7 and lat <= 53.2 and lon >= -4.1 and lon <= -3.6),
            # Lake District (too mountainous)
            (lat >= 54.3 and lat <= 54.8 and lon >= -3.4 and lon <= -2.9),
        ]
        
        if any(exclusions):
            return False
        
        return True
    
    # Outside core area - allow major cities only
    major_cities = [
        # Edinburgh (Scotland)
        (lat >= 55.9 and lat <= 56.0 and lon >= -3.3 and lon <= -3.1),
        # Glasgow (Scotland)  
        (lat >= 55.8 and lat <= 55.9 and lon >= -4.4 and lon <= -4.1),
        # Newcastle/Sunderland corridor
        (lat >= 54.8 and lat <= 55.1 and lon >= -1.8 and lon <= -1.2),
        # Belfast area (Northern Ireland)
        (lat >= 54.5 and lat <= 54.7 and lon >= -6.0 and lon <= -5.8),
        # Plymouth (major southwest city)
        (lat >= 50.3 and lat <= 50.4 and lon >= -4.2 and lon <= -4.0),
        # Aberdeen (Scotland)
        (lat >= 57.1 and lat <= 57.2 and lon >= -2.2 and lon <= -2.0),
    ]
    
    return any(major_cities)

def get_population_density_score(lat: float, lon: float) -> float:
    """Get population density score for coordinates."""
    major_cities = [
        # London area (highest population)
        {'lat': 51.5074, 'lon': -0.1278, 'score': 100.0, 'radius': 0.3},
        # Birmingham
        {'lat': 52.4862, 'lon': -1.8904, 'score': 80.0, 'radius': 0.2},
        # Manchester
        {'lat': 53.4808, 'lon': -2.2426, 'score': 75.0, 'radius': 0.2},
        # Liverpool
        {'lat': 53.4084, 'lon': -2.9916, 'score': 70.0, 'radius': 0.15},
        # Leeds
        {'lat': 53.8008, 'lon': -1.5491, 'score': 65.0, 'radius': 0.15},
        # Sheffield
        {'lat': 53.3811, 'lon': -1.4701, 'score': 60.0, 'radius': 0.1},
        # Bristol
        {'lat': 51.4545, 'lon': -2.5879, 'score': 55.0, 'radius': 0.15},
        # Newcastle
        {'lat': 54.9783, 'lon': -1.6178, 'score': 50.0, 'radius': 0.1},
        # Nottingham
        {'lat': 52.9548, 'lon': -1.1581, 'score': 45.0, 'radius': 0.1},
        # Leicester
        {'lat': 52.6369, 'lon': -1.1398, 'score': 40.0, 'radius': 0.1},
    ]
    
    max_score = 0.0
    for city in major_cities:
        distance = ((lat - city['lat'])**2 + (lon - city['lon'])**2)**0.5
        if distance <= city['radius']:
            # Score decreases with distance from city center
            score = city['score'] * (1 - distance / city['radius'])
            max_score = max(max_score, score)
    
    return max_score

def load_word_list() -> List[str]:
    """Load optimized word list from existing files."""
    try:
        with open('../word-data/norvig-word-list.txt', 'r', encoding='utf-8') as f:
            words = [word.strip() for word in f.readlines() if word.strip()]
    except FileNotFoundError:
        print("Using basic word list")
        words = ['apple', 'beach', 'chair', 'dance', 'earth', 'flame', 'green', 'house']
    
    # Filter to reasonable words (3-8 characters, alphabetic)
    filtered_words = []
    for word in words:
        if 3 <= len(word) <= 8 and word.isalpha() and word.islower():
            filtered_words.append(word)
    
    return filtered_words[:12000]  # Limit to 12k good words

def calculate_coordinate_ranges():
    """Calculate the actual coordinate index ranges needed."""
    lat_count = int((LAT_MAX - LAT_MIN) / STEP) + 1
    lon_count = int((LON_MAX - LON_MIN) / STEP) + 1
    max_index = max(lat_count, lon_count)
    
    print(f"Latitude indices: 0 to {lat_count-1}")
    print(f"Longitude indices: 0 to {lon_count-1}")
    print(f"Maximum index needed: {max_index-1}")
    
    return lat_count, lon_count, max_index

def create_index_validity_map():
    """
    Create a map of which indices are valid for both latitude and longitude.
    An index is valid if it maps to valid UK land for EITHER lat OR lon coordinates.
    """
    lat_count, lon_count, max_index = calculate_coordinate_ranges()
    
    # Track which indices are valid
    valid_indices = set()
    
    print("Analyzing latitude indices...")
    # Check latitude indices (longitude fixed at center)
    center_lon = (LON_MIN + LON_MAX) / 2
    for lat_idx in range(lat_count):
        lat = LAT_MIN + lat_idx * STEP
        if is_valid_uk_land(lat, center_lon):
            valid_indices.add(lat_idx)
    
    print("Analyzing longitude indices...")
    # Check longitude indices (latitude fixed at center)  
    center_lat = (LAT_MIN + LAT_MAX) / 2
    for lon_idx in range(lon_count):
        lon = LON_MIN + lon_idx * STEP
        if is_valid_uk_land(center_lat, lon):
            valid_indices.add(lon_idx)
    
    print("Analyzing coordinate combinations for population scores...")
    # Also include indices that are part of high-population coordinate pairs
    high_pop_indices = set()
    sample_step = 100  # Sample every 100th coordinate to avoid exhaustive search
    
    for lat_idx in range(0, lat_count, sample_step):
        for lon_idx in range(0, lon_count, sample_step):
            lat = LAT_MIN + lat_idx * STEP
            lon = LON_MIN + lon_idx * STEP
            
            if is_valid_uk_land(lat, lon):
                pop_score = get_population_density_score(lat, lon)
                if pop_score > 10:  # High population area
                    high_pop_indices.add(lat_idx)
                    high_pop_indices.add(lon_idx)
    
    valid_indices.update(high_pop_indices)
    
    print(f"Found {len(valid_indices)} valid indices out of {max_index}")
    
    return valid_indices, max_index

def create_optimized_word_list():
    """Create the final optimized word list."""
    words = load_word_list()
    valid_indices, max_index = create_index_validity_map()
    
    # Create word list with INVALID markers
    word_list = [INVALID_MARKER] * WORDS_NEEDED
    
    # Assign words to valid indices
    word_idx = 0
    for i in sorted(valid_indices):
        if i < WORDS_NEEDED and word_idx < len(words):
            word_list[i] = words[word_idx]
            word_idx += 1
    
    # Count results
    valid_count = sum(1 for w in word_list if w != INVALID_MARKER)
    invalid_count = len(word_list) - valid_count
    
    print(f"Created word list: {valid_count:,} valid words, {invalid_count:,} invalid positions")
    
    # Test key locations
    test_locations = [
        ("London", 51.5074, -0.1278),
        ("Manchester", 53.4808, -2.2426),
        ("Birmingham", 52.4862, -1.8904),
        ("Celtic Sea", 51.0, -6.0),
    ]
    
    print("\nTesting key locations:")
    for name, lat, lon in test_locations:
        lat_idx = int((lat - LAT_MIN) / STEP)
        lon_idx = int((lon - LON_MIN) / STEP)
        
        lat_word = word_list[lat_idx] if lat_idx < len(word_list) else "OUT_OF_RANGE"
        lon_word = word_list[lon_idx] if lon_idx < len(word_list) else "OUT_OF_RANGE"
        
        is_valid = lat_word != INVALID_MARKER and lon_word != INVALID_MARKER
        print(f"  {name}: lat_idx={lat_idx} ({lat_word}), lon_idx={lon_idx} ({lon_word}) -> {'VALID' if is_valid else 'INVALID'}")
    
    return word_list

def save_word_list(words: List[str]):
    """Save the word list to files."""
    # Save as text file
    with open('fixed_geo_words.txt', 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")
    
    # Save as zip file
    with zipfile.ZipFile('geo_validated_words.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('geo_validated_words.txt', '\n'.join(words))
    
    print("Saved fixed word list to geo_validated_words.zip")

if __name__ == "__main__":
    print("Creating fixed geographic word list...")
    word_list = create_optimized_word_list()
    save_word_list(word_list)
    print("Done!")
