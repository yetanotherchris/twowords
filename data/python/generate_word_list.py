def ensure_polygon():
    if not os.path.exists(POLY_WKT_ZIP):
        download_polygon()
import os
import json
import zipfile
import urllib.request
from shapely import wkt
from shapely.geometry import LineString, shape

# Coordinate settings (match the C# service)
LAT_MIN = 49.0
LAT_MAX = 60.0
LON_MIN = -8.0
LON_MAX = 2.0
STEP = 0.0001
LAT_COUNT = int((LAT_MAX - LAT_MIN) / STEP) + 1
LON_COUNT = int((LON_MAX - LON_MIN) / STEP) + 1

INVALID_POINT = "INVALID_POINT"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
WORDS_DIR = os.path.join(DATA_DIR, "words")
POLYGONS_DIR = os.path.join(DATA_DIR, "polygons")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
POLY_WKT_ZIP = os.path.join(POLYGONS_DIR, "uk_polygon.wkt.zip")
POLY_WKT_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/GBR.geo.json"
WORDS_TXT = os.path.join(OUTPUT_DIR, "words.txt")


def download_polygon():
    """Download UK polygon GeoJSON and save as zipped WKT."""
    with urllib.request.urlopen(POLY_WKT_URL) as resp:
        geojson = json.load(resp)
    geometry = shape(geojson["features"][0]["geometry"])
    wkt_str = geometry.wkt
    os.makedirs(POLYGONS_DIR, exist_ok=True)
    with zipfile.ZipFile(POLY_WKT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("uk_polygon.wkt", wkt_str)

def load_polygon():
    ensure_polygon()
    with zipfile.ZipFile(POLY_WKT_ZIP, "r") as z:
        with z.open("uk_polygon.wkt") as f:
            data = f.read().decode("utf-8")
    return wkt.loads(data)




def lat_intersects(poly, lat):
    line = LineString([(LON_MIN, lat), (LON_MAX, lat)])
    return poly.intersects(line)


def lon_intersects(poly, lon):
    line = LineString([(lon, LAT_MIN), (lon, LAT_MAX)])
    return poly.intersects(line)


def main():
    poly = load_polygon()
    max_count = max(LAT_COUNT, LON_COUNT)
    words_file = os.path.join(WORDS_DIR, "words.txt")
    if not os.path.exists(words_file):
        raise FileNotFoundError(f"Word list file not found: {words_file}\nPlease generate it using score_words.py and place it in the correct location.")
    print(f"Loading base words from {words_file}...")
    with open(words_file, "r", encoding="utf-8") as f:
        base_words = [line.strip() for line in f if line.strip()]

    results = []
    from shapely.geometry import Point
    for i in range(max_count):
        lat = LAT_MIN + i * STEP if i < LAT_COUNT else LAT_MIN
        lon = LON_MIN + i * STEP if i < LON_COUNT else LON_MIN
        point = Point(lon, lat)
        if not poly.contains(point):
            results.append(INVALID_POINT)
        else:
            results.append(base_words[i])

    # Validate output word list length
    expected_count = max_count
    actual_count = len(results)
    if actual_count != expected_count:
        raise RuntimeError(f"Output word list has {actual_count} entries, expected {expected_count}.")

    txt_content = "\n".join(results)
    # Write words.txt to output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(WORDS_TXT, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"Wrote {WORDS_TXT}")

    # Verify a range of words in words.txt
    sample_words = [w for w in results if w != INVALID_POINT][:20]
    print("Sample of first 20 valid words:", sample_words)


if __name__ == "__main__":
    main()
