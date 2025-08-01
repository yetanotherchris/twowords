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
"""
Module for polygon filtering logic. Use PolygonUtils from twowords_utils.polygon_utils.
No main logic here; use twowords_cli.py for CLI entry points.
"""
def load_polygon():
