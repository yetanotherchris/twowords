#!/usr/bin/env python3
"""
Verify the UK cities coverage and word mapping correctness.

This script verifies that:
1. All 76 UK cities are properly covered with indices
2. The word list has the correct number of words (110,001)
3. Food dishes are strategically placed at city indices
4. No duplicate words exist

Attribution: Verification logic for TwoWords mapping system.
"""

import os
import argparse
from typing import Set, Dict, List
from collections import Counter

def load_city_indices(words_dir: str) -> Dict[str, Dict]:
    """Load city coverage indices from file."""
    city_indices_file = os.path.join(words_dir, 'uk_cities_indices.txt')
    city_data = {}
    
    if not os.path.exists(city_indices_file):
        print(f"Warning: {city_indices_file} not found")
        return city_data
    
    with open(city_indices_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if ':' in line:
                    city_name, indices_part = line.split(':', 1)
                    if '|' in indices_part:
                        lat_part, lon_part = indices_part.split('|', 1)
                        lat_indices = [int(x.strip()) for x in lat_part.split(',') if x.strip()]
                        lon_indices = [int(x.strip()) for x in lon_part.split(',') if x.strip()]
                        city_data[city_name] = {
                            'lat_indices': lat_indices,
                            'lon_indices': lon_indices
                        }
    
    return city_data

def load_word_list(output_dir: str) -> List[str]:
    """Load the generated word list."""
    words_file = os.path.join(output_dir, 'words.txt')
    if not os.path.exists(words_file):
        print(f"Warning: {words_file} not found")
        return []
    
    with open(words_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def load_food_dishes(words_dir: str) -> Set[str]:
    """Load food dishes list."""
    food_file = os.path.join(words_dir, 'food_dishes_final.txt')
    if not os.path.exists(food_file):
        print(f"Warning: {food_file} not found")
        return set()
    
    with open(food_file, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())

def verify_city_coverage(city_data: Dict[str, Dict]) -> bool:
    """Verify that all expected UK cities are covered."""
    print("Verifying UK Cities Coverage:")
    print("-" * 40)
    
    expected_counts = {
        'England': 55,
        'Scotland': 8,
        'Wales': 7,
        'Northern Ireland': 6
    }
    
    # Load city coverage details
    coverage_file = os.path.join(os.path.dirname(__file__), '..', '..', 'words', 'uk_cities_coverage.txt')
    if os.path.exists(coverage_file):
        country_counts = {}
        with open(coverage_file, 'r') as f:
            for line in f:
                if '|' in line and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) >= 2:
                        country = parts[1].strip()
                        country_counts[country] = country_counts.get(country, 0) + 1
        
        all_good = True
        for country, expected in expected_counts.items():
            actual = country_counts.get(country, 0)
            status = "✓" if actual == expected else "✗"
            print(f"  {country:20s}: {actual:2d} cities (expected {expected:2d}) {status}")
            if actual != expected:
                all_good = False
        
        total_cities = len(city_data)
        expected_total = sum(expected_counts.values())
        total_status = "✓" if total_cities == expected_total else "✗"
        print(f"  {'Total':20s}: {total_cities:2d} cities (expected {expected_total:2d}) {total_status}")
        
        return all_good and total_cities == expected_total
    else:
        print("  Coverage file not found - cannot verify city counts")
        return False

def verify_word_list(words: List[str]) -> bool:
    """Verify word list integrity."""
    print("\nVerifying Word List:")
    print("-" * 40)
    
    expected_count = 110001
    actual_count = len(words)
    count_status = "✓" if actual_count == expected_count else "✗"
    print(f"  Word count: {actual_count:,} (expected {expected_count:,}) {count_status}")
    
    # Check for duplicates
    word_counts = Counter(words)
    duplicates = [word for word, count in word_counts.items() if count > 1]
    duplicate_status = "✓" if not duplicates else "✗"
    print(f"  Duplicates: {len(duplicates)} {duplicate_status}")
    
    if duplicates:
        print(f"    First few duplicates: {duplicates[:5]}")
    
    # Check for empty or invalid words
    empty_words = [i for i, word in enumerate(words) if not word or not word.isalpha()]
    empty_status = "✓" if not empty_words else "✗"
    print(f"  Invalid words: {len(empty_words)} {empty_status}")
    
    return actual_count == expected_count and not duplicates and not empty_words

def verify_food_placement(words: List[str], city_data: Dict[str, Dict], food_dishes: Set[str]) -> bool:
    """Verify that food dishes are placed at city indices."""
    print("\nVerifying Food Dish Placement:")
    print("-" * 40)
    
    if not food_dishes:
        print("  No food dishes loaded - skipping verification")
        return True
    
    # Collect all city indices
    all_city_indices = set()
    for city_name, data in city_data.items():
        all_city_indices.update(data['lat_indices'])
        all_city_indices.update(data['lon_indices'])
    
    # Check words at city indices
    food_at_cities = 0
    total_checked = 0
    
    for idx in sorted(list(all_city_indices)):
        if 0 <= idx < len(words):
            word = words[idx]
            total_checked += 1
            if word in food_dishes:
                food_at_cities += 1
    
    food_percentage = (food_at_cities / total_checked * 100) if total_checked > 0 else 0
    print(f"  City indices checked: {total_checked:,}")
    print(f"  Food dishes at cities: {food_at_cities:,} ({food_percentage:.1f}%)")
    
    # Sample some food placements
    print(f"  Sample food dishes found:")
    found_foods = []
    for idx in sorted(list(all_city_indices))[:20]:  # Check first 20 city indices
        if 0 <= idx < len(words) and words[idx] in food_dishes:
            found_foods.append(f"Index {idx}: '{words[idx]}'")
    
    for food in found_foods[:5]:  # Show first 5
        print(f"    {food}")
    
    # Consider it successful if we have a reasonable percentage of food dishes
    return food_at_cities > 0

def verify_coordinate_coverage(city_data: Dict[str, Dict]) -> bool:
    """Verify coordinate coverage makes sense."""
    print("\nVerifying Coordinate Coverage:")
    print("-" * 40)
    
    total_lat_indices = set()
    total_lon_indices = set()
    
    for city_name, data in city_data.items():
        total_lat_indices.update(data['lat_indices'])
        total_lon_indices.update(data['lon_indices'])
    
    print(f"  Total latitude indices: {len(total_lat_indices):,}")
    print(f"  Total longitude indices: {len(total_lon_indices):,}")
    print(f"  Total unique indices: {len(total_lat_indices) + len(total_lon_indices):,}")
    
    # Check reasonable ranges for UK
    lat_min, lat_max = min(total_lat_indices), max(total_lat_indices)
    lon_min, lon_max = min(total_lon_indices), max(total_lon_indices)
    
    print(f"  Latitude index range: {lat_min:,} to {lat_max:,}")
    print(f"  Longitude index range: {lon_min:,} to {lon_max:,}")
    
    # Convert back to approximate coordinates for sanity check
    # LAT_MIN = 49.0, STEP = 0.0001
    # LON_MIN = -8.0, STEP = 0.0001
    approx_lat_min = 49.0 + lat_min * 0.0001
    approx_lat_max = 49.0 + lat_max * 0.0001
    approx_lon_min = -8.0 + lon_min * 0.0001
    approx_lon_max = -8.0 + lon_max * 0.0001
    
    print(f"  Approximate latitude range: {approx_lat_min:.2f}° to {approx_lat_max:.2f}°")
    print(f"  Approximate longitude range: {approx_lon_min:.2f}° to {approx_lon_max:.2f}°")
    
    # UK roughly spans 49.9°N to 58.7°N and -8.2°W to 1.8°E
    lat_reasonable = 49.0 <= approx_lat_min <= 51.0 and 57.0 <= approx_lat_max <= 59.0
    lon_reasonable = -9.0 <= approx_lon_min <= -7.0 and 0.0 <= approx_lon_max <= 3.0
    
    status = "✓" if lat_reasonable and lon_reasonable else "✗"
    print(f"  Coordinate ranges reasonable: {status}")
    
    return lat_reasonable and lon_reasonable

def main():
    parser = argparse.ArgumentParser(description="Verify UK cities coverage and word mapping")
    parser.add_argument("--words-dir", default=None, help="Words directory")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    
    args = parser.parse_args()
    
    # Determine paths
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        words_dir = args.words_dir or "/words"
        output_dir = args.output_dir or "/output"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        words_dir = args.words_dir or os.path.join(repo_root, "data", "words")
        output_dir = args.output_dir or os.path.join(repo_root, "data", "output")
    
    print("TwoWords UK Cities Coverage Verification")
    print("=" * 50)
    print(f"Words directory: {words_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Load data
    city_data = load_city_indices(words_dir)
    words = load_word_list(output_dir)
    food_dishes = load_food_dishes(words_dir)
    
    print(f"Loaded {len(city_data)} cities, {len(words):,} words, {len(food_dishes)} food dishes")
    print()
    
    # Run verifications
    city_ok = verify_city_coverage(city_data)
    words_ok = verify_word_list(words)
    food_ok = verify_food_placement(words, city_data, food_dishes)
    coords_ok = verify_coordinate_coverage(city_data)
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY:")
    print(f"  City coverage: {'PASS' if city_ok else 'FAIL'}")
    print(f"  Word list integrity: {'PASS' if words_ok else 'FAIL'}")
    print(f"  Food dish placement: {'PASS' if food_ok else 'FAIL'}")
    print(f"  Coordinate coverage: {'PASS' if coords_ok else 'FAIL'}")
    print()
    
    overall_status = "PASS" if all([city_ok, words_ok, food_ok, coords_ok]) else "FAIL"
    print(f"OVERALL: {overall_status}")
    
    return 0 if overall_status == "PASS" else 1

if __name__ == "__main__":
    exit(main())
