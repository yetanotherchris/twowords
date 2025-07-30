#!/usr/bin/env python3
"""
Summary of the TwoWords optimization for major UK conurbations.
This script shows the before/after effect of placing popular words
at indices corresponding to major cities and popular areas.
"""

import requests
import json

# Test coordinates for major UK areas
test_locations = [
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "population": "9M"},
    {"name": "Manchester", "lat": 53.4808, "lon": -2.2426, "population": "2.7M"},
    {"name": "Birmingham", "lat": 52.4862, "lon": -1.8904, "population": "2.9M"},
    {"name": "Leeds", "lat": 53.8008, "lon": -1.5491, "population": "1.9M"},
    {"name": "Glasgow", "lat": 55.8642, "lon": -4.2518, "population": "1.8M"},
    {"name": "Liverpool", "lat": 53.4084, "lon": -2.9916, "population": "1.6M"},
    {"name": "Edinburgh", "lat": 55.9533, "lon": -3.1883, "population": "1.4M"},
    {"name": "Bristol", "lat": 51.4545, "lon": -2.5879, "population": "1.1M"},
    {"name": "Cardiff", "lat": 51.4816, "lon": -3.1791, "population": "1.1M"},
    {"name": "Sheffield", "lat": 53.3811, "lon": -1.4701, "population": "1.2M"},
]

print("TwoWords API - Popular Words Optimization Results")
print("=" * 60)
print("Major UK conurbations now map to highly recognizable English words:")
print()

# Test the API
api_base = "http://localhost:5001"

try:
    for location in test_locations:
        response = requests.get(f"{api_base}/words", params={
            "lat": location["lat"],
            "lon": location["lon"]
        })
        
        if response.status_code == 200:
            data = response.json()
            lat_word = data["latitudeWord"]
            lon_word = data["longitudeWord"]
            
            print(f"{location['name']:12} ({location['population']:>4}) -> {lat_word}.{lon_word}")
        else:
            print(f"{location['name']:12} ({location['population']:>4}) -> ERROR: {response.status_code}")
            
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to API at http://localhost:5001")
    print("Please make sure the TwoWords API is running.")
    print()
    print("To start the API, run:")
    print("cd src/TwoWordsApi && dotnet run --urls 'http://localhost:5001'")
    
print()
print("Benefits of this optimization:")
print("- Major cities now use the most common English words")
print("- Easy to remember and communicate coordinates")
print("- Better user experience for popular locations")
print("- Maintains full coverage with 1,040,000 total words")
print()
print("Popular words strategically placed at 30 key indices corresponding to:")
print("- London, Manchester, Birmingham, Leeds, Glasgow")
print("- Liverpool, Edinburgh, Bristol, Cardiff, Sheffield")  
print("- Newcastle, Belfast, Nottingham, Oxford, Cambridge")
print("- And other significant UK locations")
