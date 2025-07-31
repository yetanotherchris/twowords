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

INVALID_LAT = "INVALID_LAT"
INVALID_LON = "INVALID_LON"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORD_DIR = os.path.join(SCRIPT_DIR, "word-data")
WORD_FILE = os.path.join(WORD_DIR, "norvig-word-list.txt")
POLY_WKT_ZIP = os.path.join(WORD_DIR, "uk_polygon.wkt.zip")
POLY_WKT_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/GBR.geo.json"
OUTPUT_ZIP = os.path.join(ROOT, "expanded_words.zip")


def download_polygon():
    """Download UK polygon GeoJSON and save as zipped WKT."""
    with urllib.request.urlopen(POLY_WKT_URL) as resp:
        geojson = json.load(resp)
    geometry = shape(geojson["features"][0]["geometry"])
    wkt_str = geometry.wkt
    os.makedirs(WORD_DIR, exist_ok=True)
    with zipfile.ZipFile(POLY_WKT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("uk_polygon.wkt", wkt_str)


def ensure_polygon():
    if not os.path.exists(POLY_WKT_ZIP):
        download_polygon()


def load_polygon():
    ensure_polygon()
    with zipfile.ZipFile(POLY_WKT_ZIP, "r") as z:
        with z.open("uk_polygon.wkt") as f:
            data = f.read().decode("utf-8")
    return wkt.loads(data)


def load_words(n):
    words = []
    with open(WORD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
            if len(words) >= n:
                break
    if len(words) < n:
        raise RuntimeError("Not enough words in source list")
    return words


def lat_intersects(poly, lat):
    line = LineString([(LON_MIN, lat), (LON_MAX, lat)])
    return poly.intersects(line)


def lon_intersects(poly, lon):
    line = LineString([(lon, LAT_MIN), (lon, LAT_MAX)])
    return poly.intersects(line)


def main():
    poly = load_polygon()
    max_count = max(LAT_COUNT, LON_COUNT)
    base_words = load_words(max_count)

    results = []
    for i in range(max_count):
        lat_valid = lat_intersects(poly, LAT_MIN + i * STEP) if i < LAT_COUNT else False
        lon_valid = lon_intersects(poly, LON_MIN + i * STEP) if i < LON_COUNT else False
        if not lat_valid:
            results.append(INVALID_LAT)
        elif not lon_valid:
            results.append(INVALID_LON)
        else:
            results.append(base_words[i])

    txt_content = "\n".join(results)
    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("expanded_words.txt", txt_content)

    print(f"Wrote {OUTPUT_ZIP}")


if __name__ == "__main__":
    main()
