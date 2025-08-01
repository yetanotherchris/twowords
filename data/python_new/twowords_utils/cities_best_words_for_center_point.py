#!/usr/bin/env python3
"""
Calculate indices for all 76 official UK cities and expand to 2-mile radius areas.

This script generates coordinate indices for all officially recognized UK cities
(as granted city status by the monarch) and creates 2-mile radius coverage areas
around each city center for strategic placement of the best/most friendly words.

Attribution: City coordinates sourced from Ordnance Survey and various UK geographic databases.
"""

import os
import math
import argparse
from typing import List, Tuple, Set
from dataclasses import dataclass

@dataclass
class City:
    """Represents a UK city with its coordinates."""
    name: str
    lat: float
    lon: float
    country: str  # England, Scotland, Wales, Northern Ireland

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

def get_all_uk_cities() -> List[City]:
    """
    Get all 76 officially recognized UK cities with their coordinates.
    
    Source: Official city status granted by the monarch.
    55 in England, 8 in Scotland, 7 in Wales, 6 in Northern Ireland.
    """
    cities = [
        # England (55 cities)
        City("London", 51.5074, -0.1278, "England"),
        City("Birmingham", 52.4862, -1.8904, "England"),
        City("Leeds", 53.8008, -1.5491, "England"),
        City("Sheffield", 53.3811, -1.4701, "England"),
        City("Bradford", 53.7960, -1.7594, "England"),
        City("Liverpool", 53.4084, -2.9916, "England"),
        City("Manchester", 53.4808, -2.2426, "England"),
        City("Bristol", 51.4545, -2.5879, "England"),
        City("Newcastle upon Tyne", 54.9783, -1.6178, "England"),
        City("Nottingham", 52.9548, -1.1581, "England"),
        City("Leicester", 52.6369, -1.1398, "England"),
        City("Coventry", 52.4068, -1.5197, "England"),
        City("Hull", 53.7457, -0.3367, "England"),
        City("Plymouth", 50.3755, -4.1427, "England"),
        City("Stoke-on-Trent", 53.0027, -2.1794, "England"),
        City("Derby", 52.9225, -1.4746, "England"),
        City("Southampton", 50.9097, -1.4044, "England"),
        City("Portsmouth", 50.8198, -1.0880, "England"),
        City("York", 53.9599, -1.0873, "England"),
        City("Peterborough", 52.5695, -0.2405, "England"),
        City("Norwich", 52.6309, 1.2974, "England"),
        City("Sunderland", 54.9069, -1.3838, "England"),
        City("Oxford", 51.7520, -1.2577, "England"),
        City("Cambridge", 52.2053, 0.1218, "England"),
        City("Brighton and Hove", 50.8225, -0.1372, "England"),
        City("Exeter", 50.7184, -3.5339, "England"),
        City("Chester", 53.1906, -2.8907, "England"),
        City("Gloucester", 51.8642, -2.2381, "England"),
        City("Lancaster", 54.0466, -2.8007, "England"),
        City("Lincoln", 53.2307, -0.5406, "England"),
        City("Chichester", 50.8365, -0.7792, "England"),
        City("Worcester", 52.1929, -2.2206, "England"),
        City("Canterbury", 51.2802, 1.0789, "England"),
        City("Carlisle", 54.8951, -2.9441, "England"),
        City("Durham", 54.7753, -1.5849, "England"),
        City("Ely", 52.3980, 0.2622, "England"),
        City("Hereford", 52.0567, -2.7159, "England"),
        City("Lichfield", 52.6836, -1.8262, "England"),
        City("Ripon", 54.1381, -1.5235, "England"),
        City("Truro", 50.2632, -5.0510, "England"),
        City("Wakefield", 53.6833, -1.5000, "England"),
        City("Wells", 51.2090, -2.6469, "England"),
        City("Winchester", 51.0632, -1.3080, "England"),
        City("Salisbury", 51.0693, -1.7944, "England"),
        City("Bath", 51.3758, -2.3599, "England"),
        City("Chelmsford", 51.7356, 0.4685, "England"),
        City("Preston", 53.7632, -2.7031, "England"),
        City("Salford", 53.4875, -2.2901, "England"),
        City("Wolverhampton", 52.5855, -2.1282, "England"),
        City("Southend-on-Sea", 51.5460, 0.7077, "England"),
        City("Milton Keynes", 52.0406, -0.7594, "England"),
        City("Blackpool", 53.8175, -3.0357, "England"),
        City("Middlesbrough", 54.5742, -1.2349, "England"),
        City("Doncaster", 53.5228, -1.1285, "England"),
        City("Reading", 51.4543, -0.9781, "England"),

        # Scotland (8 cities)
        City("Glasgow", 55.8642, -4.2518, "Scotland"),
        City("Edinburgh", 55.9533, -3.1883, "Scotland"),
        City("Aberdeen", 57.1497, -2.0943, "Scotland"),
        City("Dundee", 56.4620, -2.9707, "Scotland"),
        City("Stirling", 56.1165, -3.9369, "Scotland"),
        City("Perth", 56.3962, -3.4370, "Scotland"),
        City("Inverness", 57.4778, -4.2247, "Scotland"),
        City("Elgin", 57.6493, -3.3184, "Scotland"),

        # Wales (7 cities)
        City("Cardiff", 51.4816, -3.1791, "Wales"),
        City("Swansea", 51.6214, -3.9436, "Wales"),
        City("Newport", 51.5882, -2.9977, "Wales"),
        City("Bangor (Wales)", 53.2280, -4.1287, "Wales"),
        City("St Davids", 51.8812, -5.2660, "Wales"),
        City("St Asaph", 53.2584, -3.4420, "Wales"),
        City("Wrexham", 53.0478, -2.9916, "Wales"),

        # Northern Ireland (6 cities)
        City("Belfast", 54.5973, -5.9301, "Northern Ireland"),
        City("Derry/Londonderry", 54.9966, -7.3086, "Northern Ireland"),
        City("Armagh", 54.3493, -6.6534, "Northern Ireland"),
        City("Lisburn", 54.5162, -6.0365, "Northern Ireland"),
        City("Newry", 54.1751, -6.3402, "Northern Ireland"),
        City("Bangor (Northern Ireland)", 54.6541, -5.6695, "Northern Ireland"),  # Note: Different from Welsh Bangor
    ]
    
    return cities

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in miles.
    Uses the Haversine formula.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in miles
    r = 3956
    
    return c * r

def generate_radius_points(center_lat: float, center_lon: float, radius_miles: float, num_points: int = 36) -> List[Tuple[float, float]]:
    """
    Generate points around a center coordinate within a given radius.
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude  
        radius_miles: Radius in miles
        num_points: Number of points to generate around the circumference
        
    Returns:
        List of (lat, lon) tuples representing points within the radius
    """
    points = []
    
    # Convert radius from miles to degrees (approximate)
    # 1 degree latitude ≈ 69 miles
    radius_lat = radius_miles / 69.0
    
    # Add center point
    points.append((center_lat, center_lon))
    
    # Generate points in concentric circles
    for circle_radius in [0.3, 0.6, 1.0]:  # Fractions of the full radius
        current_radius_lat = radius_lat * circle_radius
        current_radius_lon = radius_lat * circle_radius / math.cos(math.radians(center_lat))
        
        # Number of points for this circle (fewer for inner circles)
        circle_points = max(8, int(num_points * circle_radius))
        
        for i in range(circle_points):
            angle = 2 * math.pi * i / circle_points
            lat = center_lat + current_radius_lat * math.cos(angle)
            lon = center_lon + current_radius_lon * math.sin(angle)
            points.append((lat, lon))
    
    # Add some random points within the full radius for better coverage
    import random
    for _ in range(12):  # Add 12 additional random points
        # Generate random point within circle
        r = radius_miles * math.sqrt(random.random())  # Square root for uniform distribution
        theta = random.random() * 2 * math.pi
        
        # Convert to lat/lon offset
        lat_offset = (r / 69.0) * math.cos(theta)
        lon_offset = (r / 69.0) * math.sin(theta) / math.cos(math.radians(center_lat))
        
        lat = center_lat + lat_offset
        lon = center_lon + lon_offset
        points.append((lat, lon))
    
    return points

def calculate_city_indices_with_radius(cities: List[City], radius_miles: float = 2.0) -> Tuple[Set[int], Set[int], dict]:
    """
    Calculate indices for all cities and their surrounding 2-mile radius areas.
    
    Returns:
        Tuple of (lat_indices, lon_indices, city_coverage_map)
    """
    lat_indices = set()
    lon_indices = set()
    city_coverage_map = {}  # Maps city name to list of indices
    
    print(f"Calculating indices for {len(cities)} UK cities with {radius_miles}-mile radius coverage:")
    print("-" * 80)
    
    for city in cities:
        city_lat_indices = set()
        city_lon_indices = set()
        
        # Generate points within the radius
        radius_points = generate_radius_points(city.lat, city.lon, radius_miles)
        
        print(f"\n{city.name} ({city.country}):")
        print(f"  Center: {city.lat:.4f}, {city.lon:.4f}")
        print(f"  Generated {len(radius_points)} coverage points within {radius_miles} miles")
        
        # Calculate indices for all points in the radius
        for lat, lon in radius_points:
            lat_idx = calculate_lat_index(lat)
            lon_idx = calculate_lon_index(lon)
            
            city_lat_indices.add(lat_idx)
            city_lon_indices.add(lon_idx)
            lat_indices.add(lat_idx)
            lon_indices.add(lon_idx)
        
        city_coverage_map[city.name] = {
            'lat_indices': sorted(city_lat_indices),
            'lon_indices': sorted(city_lon_indices),
            'country': city.country,
            'center_lat': city.lat,
            'center_lon': city.lon
        }
        
        print(f"  Coverage: {len(city_lat_indices)} lat indices, {len(city_lon_indices)} lon indices")
    
    return lat_indices, lon_indices, city_coverage_map

def save_indices_and_coverage(output_dir: str, lat_indices: Set[int], lon_indices: Set[int], 
                             city_coverage_map: dict, radius_miles: float):
    """Save the calculated indices and city coverage information."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the main important_indices.txt file
    indices_file = os.path.join(output_dir, "important_indices.txt")
    with open(indices_file, 'w', encoding='utf-8') as f:
        f.write(f"# Important latitude indices for all 76 UK cities ({radius_miles}-mile radius coverage)\n")
        f.write("# Generated by cities_best_words_for_center_point.py\n")
        f.write("# Attribution: City coordinates from Ordnance Survey and UK geographic databases\n")
        for idx in sorted(lat_indices):
            f.write(f"{idx}\n")
        f.write(f"# Important longitude indices for all 76 UK cities ({radius_miles}-mile radius coverage)\n")
        for idx in sorted(lon_indices):
            f.write(f"{idx}\n")
    
    # Save detailed city coverage information
    coverage_file = os.path.join(output_dir, "uk_cities_coverage.txt")
    with open(coverage_file, 'w', encoding='utf-8') as f:
        f.write(f"# UK Cities Coverage Map - {radius_miles}-mile radius per city\n")
        f.write("# Generated by cities_best_words_for_center_point.py\n")
        f.write("# Format: City Name | Country | Center Lat,Lon | Lat Indices Count | Lon Indices Count\n")
        f.write("#" + "="*80 + "\n\n")
        
        # Group by country
        countries = {}
        for city_name, data in city_coverage_map.items():
            country = data['country']
            if country not in countries:
                countries[country] = []
            countries[country].append((city_name, data))
        
        for country in ["England", "Scotland", "Wales", "Northern Ireland"]:
            if country in countries:
                f.write(f"# {country} ({len(countries[country])} cities)\n")
                f.write("-" * 40 + "\n")
                
                for city_name, data in sorted(countries[country]):
                    lat_count = len(data['lat_indices'])
                    lon_count = len(data['lon_indices'])
                    f.write(f"{city_name} | {country} | {data['center_lat']:.4f},{data['center_lon']:.4f} | {lat_count} lat | {lon_count} lon\n")
                f.write("\n")
    
    # Save machine-readable city indices
    city_indices_file = os.path.join(output_dir, "uk_cities_indices.txt")
    with open(city_indices_file, 'w', encoding='utf-8') as f:
        f.write("# Machine-readable city indices for TwoWords API\n")
        f.write("# Format: CITY_NAME:LAT_INDEX1,LAT_INDEX2|LON_INDEX1,LON_INDEX2\n")
        for city_name, data in sorted(city_coverage_map.items()):
            lat_indices_str = ','.join(map(str, data['lat_indices']))
            lon_indices_str = ','.join(map(str, data['lon_indices']))
            f.write(f"{city_name}:{lat_indices_str}|{lon_indices_str}\n")
    
    return indices_file, coverage_file, city_indices_file

def main():
    parser = argparse.ArgumentParser(description="Calculate indices for all 76 UK cities with radius coverage")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--radius", type=float, default=2.0, help="Radius in miles around each city (default: 2.0)")
    parser.add_argument("--verify", action="store_true", help="Verify the generated indices")
    
    args = parser.parse_args()
    
    # Determine output path
    if os.path.exists("/python") and os.path.exists("/words"):
        # Running in container
        output_dir = args.output_dir or "/words"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        output_dir = args.output_dir or os.path.join(repo_root, "data", "words")
    
    print("TwoWords API - UK Cities Best Words Coverage Calculator")
    print("=" * 60)
    print(f"Radius: {args.radius} miles per city")
    print(f"Output directory: {output_dir}")
    print()
    
    # Get all UK cities
    cities = get_all_uk_cities()
    
    # Verify we have the correct number of cities
    england_cities = [c for c in cities if c.country == "England"]
    scotland_cities = [c for c in cities if c.country == "Scotland"]
    wales_cities = [c for c in cities if c.country == "Wales"]
    ni_cities = [c for c in cities if c.country == "Northern Ireland"]
    
    print(f"Cities loaded:")
    print(f"  England: {len(england_cities)} (expected: 55)")
    print(f"  Scotland: {len(scotland_cities)} (expected: 8)")
    print(f"  Wales: {len(wales_cities)} (expected: 7)")
    print(f"  Northern Ireland: {len(ni_cities)} (expected: 6)")
    print(f"  Total: {len(cities)} (expected: 76)")
    
    if len(cities) != 76:
        print(f"WARNING: Expected 76 cities, but found {len(cities)}")
    
    # Calculate indices with radius coverage
    lat_indices, lon_indices, city_coverage_map = calculate_city_indices_with_radius(cities, args.radius)
    
    # Save results
    indices_file, coverage_file, city_indices_file = save_indices_and_coverage(
        output_dir, lat_indices, lon_indices, city_coverage_map, args.radius
    )
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Total latitude indices: {len(lat_indices):,}")
    print(f"  Total longitude indices: {len(lon_indices):,}")
    print(f"  Total unique indices: {len(lat_indices) + len(lon_indices):,}")
    print(f"  Coverage radius: {args.radius} miles per city")
    print()
    print("Files generated:")
    print(f"  1. {indices_file}")
    print(f"  2. {coverage_file}")
    print(f"  3. {city_indices_file}")
    
    if args.verify:
        print("\nVerification:")
        # Basic verification - check a few known cities
        test_cities = ["London", "Edinburgh", "Cardiff", "Belfast"]
        for city_name in test_cities:
            if city_name in city_coverage_map:
                data = city_coverage_map[city_name]
                print(f"  {city_name}: {len(data['lat_indices'])} lat, {len(data['lon_indices'])} lon indices")

if __name__ == "__main__":
    main()
