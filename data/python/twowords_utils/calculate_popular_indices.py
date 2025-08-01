#!/usr/bin/env python3
"""
Calculate popular indices for major UK population centers.

This script calculates the coordinate indices that correspond to major UK cities
and population centers for strategic word placement.
"""

import os
import argparse

def calculate_lat_index(lat: float) -> int:
    """Calculate latitude index from latitude value."""
    LAT_MIN = 49.0
    STEP = 0.0001
    return int((lat - LAT_MIN) / STEP)

def calculate_lon_index(lon: float) -> int:
    """Calculate longitude index from longitude value."""
    LON_MIN = -8.0
    STEP = 0.0001
    return int((lon - LON_MIN) / STEP)

def get_major_uk_cities():
    """Get coordinates of major UK cities and population centers."""
    # Major UK cities with their approximate coordinates
    cities = [
        ("London", 51.5074, -0.1278),
        ("Birmingham", 51.4816, -1.8998),
        ("Leeds", 53.8008, -1.5491),
        ("Glasgow", 55.8642, -4.2518),
        ("Sheffield", 53.3811, -1.4701),
        ("Bradford", 53.7960, -1.7594),
        ("Liverpool", 53.4084, -2.9916),
        ("Edinburgh", 55.9533, -3.1883),
        ("Manchester", 53.4808, -2.2426),
        ("Bristol", 51.4545, -2.5879),
        ("Kirklees", 53.5933, -1.8009),
        ("Fife", 56.2139, -3.1386),
        ("Wirral", 53.3727, -3.0738),
        ("North Lanarkshire", 55.8175, -3.9837),
        ("Wakefield", 53.6833, -1.5000),
        ("Cardiff", 51.4816, -3.1791),
        ("Dudley", 52.5120, -2.0814),
        ("Wigan", 53.5450, -2.6318),
        ("East Riding", 53.8429, -0.4445),
        ("South Lanarkshire", 55.6744, -3.7896),
    ]
    return cities

def main():
    parser = argparse.ArgumentParser(description="Calculate indices for major UK population centers")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    
    args = parser.parse_args()
    
    # Determine output path
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        output_dir = args.output_dir or "/words"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        output_dir = args.output_dir or os.path.join(repo_root, "data", "words")
    
    print("TwoWords API - Popular Indices Calculator")
    print("=" * 50)
    
    cities = get_major_uk_cities()
    lat_indices = set()
    lon_indices = set()
    
    print("Calculating indices for major UK cities:")
    for name, lat, lon in cities:
        lat_idx = calculate_lat_index(lat)
        lon_idx = calculate_lon_index(lon)
        lat_indices.add(lat_idx)
        lon_indices.add(lon_idx)
        print(f"  {name:20s}: lat={lat:8.4f} (idx={lat_idx:6d}), lon={lon:8.4f} (idx={lon_idx:6d})")
    
    # Save indices to file
    output_file = os.path.join(output_dir, "important_indices.txt")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Important latitude indices for major UK conurbations\n")
        for idx in sorted(lat_indices):
            f.write(f"{idx}\n")
        f.write("# Important longitude indices for major UK conurbations\n")
        for idx in sorted(lon_indices):
            f.write(f"{idx}\n")
    
    print(f"\nSaved {len(lat_indices)} latitude indices and {len(lon_indices)} longitude indices to {output_file}")
    print(f"Total unique indices: {len(lat_indices) + len(lon_indices)}")

if __name__ == "__main__":
    main()
