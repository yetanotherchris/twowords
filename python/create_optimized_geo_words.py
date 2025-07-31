#!/usr/bin/env python3
"""
Create geographically-validated word list using hardcoded UK boundaries
and population-based word optimization.
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
    """
    Enhanced UK land validation using more precise geographic rules.
    Based on your original suggestion to focus on densely populated areas.
    """
    
    # Core UK population rectangle (covers ~80% of UK population)
    # This is the densely populated corridor you mentioned:
    # Manchester longitude down to Brighton, Liverpool latitude to Essex latitude
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
        # Edinburgh
        {'lat': 55.9533, 'lon': -3.1883, 'score': 50.0, 'radius': 0.1},
        # Glasgow
        {'lat': 55.8642, 'lon': -4.2518, 'score': 45.0, 'radius': 0.1},
        # Cardiff
        {'lat': 51.4816, 'lon': -3.1791, 'score': 40.0, 'radius': 0.1},
        # Belfast
        {'lat': 54.5973, 'lon': -5.9301, 'score': 35.0, 'radius': 0.1},
    ]
    
    max_score = 0.0
    for city in major_cities:
        distance = ((lat - city['lat'])**2 + (lon - city['lon'])**2)**0.5
        if distance <= city['radius']:
            score = city['score'] * (1 - distance / city['radius'])
            max_score = max(max_score, score)
    
    # Base score for any valid UK land
    if max_score == 0.0:
        max_score = 10.0
    
    return max_score

@dataclass
class WordQuality:
    word: str
    score: float
    length: int
    is_memorable: bool
    is_common: bool
    is_funny: bool
    is_food: bool

def load_word_categories():
    """Load different categories of words for optimization."""
    categories = {
        'food_dishes': set(),
        'common_words': set(),
        'funny_words': set(),
        'memorable_words': set()
    }
    
    # Load food dishes
    food_file = '../word-data/food_dishes_final.txt'
    try:
        with open(food_file, 'r', encoding='utf-8') as f:
            categories['food_dishes'] = {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Warning: {food_file} not found")
    
    # Define memorable words (short, catchy, easy to remember)
    categories['memorable_words'] = {
        'cat', 'dog', 'sun', 'moon', 'star', 'fire', 'ice', 'gold', 'blue', 'red',
        'big', 'fun', 'yes', 'wow', 'top', 'win', 'new', 'old', 'hot', 'cool',
        'car', 'bike', 'boat', 'tree', 'rock', 'hill', 'lake', 'park', 'home',
        'love', 'hope', 'joy', 'peace', 'happy', 'lucky', 'magic', 'sweet',
        'apple', 'lemon', 'grape', 'berry', 'honey', 'sugar', 'cream', 'cheese'
    }
    
    # Common English words
    categories['common_words'] = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'man', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
        'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
    }
    
    # Potentially funny or attention-grabbing words
    categories['funny_words'] = {
        'loud', 'fart', 'burp', 'giggle', 'silly', 'crazy', 'funny', 'weird',
        'odd', 'quirky', 'goofy', 'wacky', 'zany', 'bonkers', 'mad', 'wild'
    }
    
    return categories

def calculate_word_quality(word: str, categories: Dict[str, Set[str]]) -> WordQuality:
    """Calculate comprehensive word quality score."""
    length = len(word)
    is_memorable = word in categories['memorable_words']
    is_common = word in categories['common_words']
    is_funny = word in categories['funny_words']
    is_food = word in categories['food_dishes']
    
    # Base score
    score = 50.0
    
    # Length scoring (prefer shorter words)
    if length <= 3:
        score += 40
    elif length <= 5:
        score += 20
    elif length <= 7:
        score += 0
    else:
        score -= 20
    
    # Category bonuses
    if is_food:
        score += 50  # Food dishes are great for memorable locations
    if is_memorable:
        score += 40  # Explicitly memorable words
    if is_funny:
        score += 35  # Funny words are memorable
    if is_common:
        score += 25  # Common words are easy to remember
    
    # Penalize difficult words
    if not re.match(r'^[a-z]+$', word):
        score -= 30
    
    # Avoid complex consonant clusters
    difficult_patterns = ['ght', 'pht', 'scht', 'tch']
    if any(pattern in word for pattern in difficult_patterns):
        score -= 15
    
    return WordQuality(word, score, length, is_memorable, is_common, is_funny, is_food)

def create_population_optimized_word_list():
    """Create word list optimized for UK population centers."""
    print("Creating population-optimized geographically-validated word list...")
    
    # Load existing word list
    with zipfile.ZipFile('../expanded_words.zip', 'r') as zip_file:
        with zip_file.open(zip_file.namelist()[0]) as f:
            all_words = [line.decode('utf-8').strip() for line in f if line.strip()]
    
    print(f"Loaded {len(all_words):,} words")
    
    # Load word categories for quality scoring
    categories = load_word_categories()
    print(f"Categories loaded: {[(k, len(v)) for k, v in categories.items()]}")
    
    # Score and sort words by quality
    print("Scoring words by quality...")
    word_qualities = []
    for word in all_words:
        if re.match(r'^[a-z]+$', word):  # Only valid English letters
            quality = calculate_word_quality(word, categories)
            word_qualities.append(quality)
    
    word_qualities.sort(key=lambda x: x.score, reverse=True)
    print(f"Scored {len(word_qualities):,} valid words")
    
    # Create index scoring based on coordinates and population
    print("Scoring coordinate indices by population density...")
    index_scores = []
    
    for i in range(WORDS_NEEDED):
        lat = LAT_MIN + (i * STEP)
        lon = LON_MIN + (i * STEP)
        
        if is_valid_uk_land(lat, lon):
            pop_score = get_population_density_score(lat, lon)
            index_scores.append((i, pop_score, lat, lon))
    
    # Sort by population score (highest first)
    index_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"Found {len(index_scores)} valid UK land indices")
    
    # Create final word list
    print("Creating final word list...")
    final_words = [INVALID_MARKER] * WORDS_NEEDED
    used_words = set()
    word_idx = 0
    
    # Assign best words to highest population indices
    for idx, pop_score, lat, lon in index_scores:
        if word_idx < len(word_qualities):
            while word_idx < len(word_qualities):
                word = word_qualities[word_idx].word
                word_idx += 1
                if word not in used_words:
                    final_words[idx] = word
                    used_words.add(word)
                    break
    
    # Count results
    valid_count = sum(1 for w in final_words if w != INVALID_MARKER)
    invalid_count = len(final_words) - valid_count
    
    print(f"Final word list: {valid_count:,} valid words, {invalid_count:,} invalid positions")
    
    return final_words

def save_validated_word_list(words: List[str]):
    """Save the geographically-validated word list."""
    output_file = 'geo_validated_words.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")
    
    print(f"Saved validated words to {output_file}")
    
    # Create zip file for the API
    zip_file = 'geo_validated_words.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('geo_validated_words.txt', '\n'.join(words))
    
    print(f"Created {zip_file}")
    
    # Statistics
    valid_count = sum(1 for w in words if w != INVALID_MARKER)
    invalid_count = len(words) - valid_count
    print(f"Statistics: {valid_count:,} valid words, {invalid_count:,} invalid positions")
    
    # Report on key word locations
    test_words = ['loud', 'fart', 'pizza', 'curry', 'fish', 'chips', 'new', 'old', 'cat', 'dog']
    print(f"\nKey word locations:")
    for word in test_words:
        if word in words:
            idx = words.index(word)
            lat = LAT_MIN + (idx * STEP)
            lon = LON_MIN + (idx * STEP)
            status = "VALID" if words[idx] != INVALID_MARKER else "INVALID"
            if status == "VALID":
                pop_score = get_population_density_score(lat, lon)
                print(f"'{word}' -> index {idx} (lat ~{lat:.4f}, lon ~{lon:.4f}, pop_score: {pop_score:.1f}) [{status}]")
            else:
                print(f"'{word}' -> index {idx} [{status}]")

if __name__ == "__main__":
    try:
        validated_words = create_population_optimized_word_list()
        save_validated_word_list(validated_words)
        print("Population-optimized geographic validation complete!")
        
        # Test some specific coordinates
        print("\nTesting specific coordinates:")
        test_coords = [
            (50.4425, -6.8670, "loud.fart location (Celtic Sea)"),
            (51.5074, -0.1278, "London"),
            (53.4808, -2.2426, "Manchester"),
            (52.4862, -1.8904, "Birmingham"),
        ]
        
        for lat, lon, name in test_coords:
            valid = is_valid_uk_land(lat, lon)
            print(f"{name}: {lat:.4f}, {lon:.4f} -> {'VALID' if valid else 'INVALID'}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
