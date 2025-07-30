#!/usr/bin/env python3
"""
Calculate word list indices for major UK conurbations and popular areas.
This will help us determine which indices should contain the most popular words.
"""

# Constants from the API
LAT_MIN = 49.0
LAT_MAX = 60.0
LON_MIN = -8.0
LON_MAX = 2.0
STEP = 0.0001

def coord_to_index(coord, min_val):
    """Convert coordinate to array index"""
    return int((coord - min_val) / STEP)

# Major UK conurbations and popular areas
major_areas = [
    # Major cities
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "population": 9_000_000},
    {"name": "Manchester", "lat": 53.4808, "lon": -2.2426, "population": 2_700_000},
    {"name": "Birmingham", "lat": 52.4862, "lon": -1.8904, "population": 2_900_000},
    {"name": "Leeds", "lat": 53.8008, "lon": -1.5491, "population": 1_900_000},
    {"name": "Glasgow", "lat": 55.8642, "lon": -4.2518, "population": 1_800_000},
    {"name": "Liverpool", "lat": 53.4084, "lon": -2.9916, "population": 1_600_000},
    {"name": "Edinburgh", "lat": 55.9533, "lon": -3.1883, "population": 1_400_000},
    {"name": "Bristol", "lat": 51.4545, "lon": -2.5879, "population": 1_100_000},
    {"name": "Cardiff", "lat": 51.4816, "lon": -3.1791, "population": 1_100_000},
    {"name": "Sheffield", "lat": 53.3811, "lon": -1.4701, "population": 1_200_000},
    {"name": "Newcastle", "lat": 54.9783, "lon": -1.6178, "population": 1_600_000},
    {"name": "Belfast", "lat": 54.5973, "lon": -5.9301, "population": 900_000},
    {"name": "Nottingham", "lat": 52.9548, "lon": -1.1581, "population": 1_200_000},
    
    # Famous landmarks that attract visitors
    {"name": "Oxford", "lat": 51.7520, "lon": -1.2577, "population": 500_000},
    {"name": "Cambridge", "lat": 52.2053, "lon": 0.1218, "population": 400_000},
    {"name": "Bath", "lat": 51.3758, "lon": -2.3599, "population": 300_000},
    {"name": "York", "lat": 53.9600, "lon": -1.0873, "population": 400_000},
    {"name": "Canterbury", "lat": 51.2802, "lon": 1.0789, "population": 200_000},
    {"name": "Stratford-upon-Avon", "lat": 52.1919, "lon": -1.7080, "population": 100_000},
    
    # Popular tourist/geographic areas
    {"name": "Brighton", "lat": 50.8225, "lon": -0.1372, "population": 600_000},
    {"name": "Bournemouth", "lat": 50.7192, "lon": -1.8808, "population": 400_000},
    {"name": "Plymouth", "lat": 50.3755, "lon": -4.1427, "population": 400_000},
    {"name": "Portsmouth", "lat": 50.8198, "lon": -1.0880, "population": 400_000},
    {"name": "Southampton", "lat": 50.9097, "lon": -1.4044, "population": 500_000},
]

print("Major UK Conurbations and Popular Areas - Index Mapping:")
print("=" * 70)

# Calculate indices for each area
area_indices = []
for area in major_areas:
    lat_index = coord_to_index(area["lat"], LAT_MIN)
    lon_index = coord_to_index(area["lon"], LON_MIN)
    
    area_indices.append({
        "name": area["name"],
        "lat_index": lat_index,
        "lon_index": lon_index,
        "population": area["population"],
        "coordinates": (area["lat"], area["lon"])
    })
    
    print(f"{area['name']:20} | Lat Index: {lat_index:6d} | Lon Index: {lon_index:6d} | Pop: {area['population']:>9,}")

# Sort by population to identify most important indices
area_indices.sort(key=lambda x: x["population"], reverse=True)

print("\nTop 15 Most Important Indices (by population):")
print("=" * 50)

important_lat_indices = set()
important_lon_indices = set()

for i, area in enumerate(area_indices[:15]):
    important_lat_indices.add(area["lat_index"])
    important_lon_indices.add(area["lon_index"])
    print(f"{i+1:2d}. {area['name']:20} | Lat: {area['lat_index']:6d} | Lon: {area['lon_index']:6d}")

print(f"\nUnique latitude indices to prioritize: {sorted(important_lat_indices)}")
print(f"Unique longitude indices to prioritize: {sorted(important_lon_indices)}")

# Calculate total coordinate range for context
lat_count = int((LAT_MAX - LAT_MIN) / STEP) + 1
lon_count = int((LON_MAX - LON_MIN) / STEP) + 1

print(f"\nTotal index ranges:")
print(f"Latitude indices: 0 to {lat_count-1} ({lat_count:,} total)")
print(f"Longitude indices: 0 to {lon_count-1} ({lon_count:,} total)")

# Save the important indices for use in the word reorganization script
with open("important_indices.txt", "w") as f:
    f.write("# Important latitude indices for major UK conurbations\n")
    for idx in sorted(important_lat_indices):
        f.write(f"{idx}\n")
    f.write("# Important longitude indices for major UK conurbations\n")
    for idx in sorted(important_lon_indices):
        f.write(f"{idx}\n")

print(f"\nImportant indices saved to 'important_indices.txt'")
