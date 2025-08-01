import os
import json
import zipfile
import urllib.request
from shapely import wkt
from shapely.geometry import LineString, shape, Point

class PolygonUtils:
    LAT_MIN = 49.0
    LAT_MAX = 60.0
    LON_MIN = -8.0
    LON_MAX = 2.0
    STEP = 0.0001
    LAT_COUNT = int((LAT_MAX - LAT_MIN) / STEP) + 1
    LON_COUNT = int((LON_MAX - LON_MIN) / STEP) + 1
    INVALID_POINT = "INVALID_POINT"

    def __init__(self, root_dir):
        self.ROOT = root_dir
        # If running in container, root_dir is "/" and everything is at /words, /output, /polygons
        if root_dir == "/":
            self.WORDS_DIR = "/words"
            self.POLYGONS_DIR = "/polygons"
            self.OUTPUT_DIR = "/output"
        else:
            self.DATA_DIR = os.path.join(self.ROOT, "data")
            self.WORDS_DIR = os.path.join(self.DATA_DIR, "words")
            self.POLYGONS_DIR = os.path.join(self.DATA_DIR, "polygons")
            self.OUTPUT_DIR = os.path.join(self.DATA_DIR, "output")
        self.POLY_WKT_ZIP = os.path.join(self.POLYGONS_DIR, "uk_polygon.wkt.zip")
        self.POLY_WKT_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/GBR.geo.json"
        self.WORDS_TXT = os.path.join(self.OUTPUT_DIR, "words.txt")

    def download_polygon(self):
        with urllib.request.urlopen(self.POLY_WKT_URL) as resp:
            geojson = json.load(resp)
        geometry = shape(geojson["features"][0]["geometry"])
        wkt_str = geometry.wkt
        os.makedirs(self.POLYGONS_DIR, exist_ok=True)
        with zipfile.ZipFile(self.POLY_WKT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("uk_polygon.wkt", wkt_str)
        # Debug: print file size after writing
        size = os.path.getsize(self.POLY_WKT_ZIP)
        print(f"[DEBUG] Polygon zip file size after download: {size} bytes at {self.POLY_WKT_ZIP}")
        # Validate the zip file after writing
        try:
            with zipfile.ZipFile(self.POLY_WKT_ZIP, "r") as z:
                test = z.namelist()
                if "uk_polygon.wkt" not in test:
                    raise RuntimeError("Polygon zip file does not contain uk_polygon.wkt")
        except Exception as e:
            raise RuntimeError(f"Polygon zip file is invalid after download: {e}")

    def validate_polygon_zip(self):
        if not os.path.exists(self.POLY_WKT_ZIP):
            raise FileNotFoundError(f"Polygon zip file not found: {self.POLY_WKT_ZIP}")
        size = os.path.getsize(self.POLY_WKT_ZIP)
        print(f"[DEBUG] Polygon zip file size before filtering: {size} bytes at {self.POLY_WKT_ZIP}")
        try:
            with zipfile.ZipFile(self.POLY_WKT_ZIP, "r") as z:
                test = z.namelist()
                if "uk_polygon.wkt" not in test:
                    raise RuntimeError("Polygon zip file does not contain uk_polygon.wkt")
        except Exception as e:
            raise RuntimeError(f"Polygon zip file is invalid before filtering: {e}")

    def ensure_polygon(self):
        if not os.path.exists(self.POLY_WKT_ZIP):
            self.download_polygon()

    def load_polygon(self):
        self.ensure_polygon()
        self.validate_polygon_zip()
        with zipfile.ZipFile(self.POLY_WKT_ZIP, "r") as z:
            with z.open("uk_polygon.wkt") as f:
                data = f.read().decode("utf-8")
        return wkt.loads(data)

    def lat_intersects(self, poly, lat):
        line = LineString([(self.LON_MIN, lat), (self.LON_MAX, lat)])
        return poly.intersects(line)

    def lon_intersects(self, poly, lon):
        line = LineString([(lon, self.LAT_MIN), (lon, self.LAT_MAX)])
        return poly.intersects(line)

    def filter_words_for_polygon(self, base_words):
        """
        Filter words by polygon, marking out-of-bounds coordinates as INVALID_POINT.
        This follows the logic from words_filter_for_polygon.py.
        """
        print("Loading polygon for filtering...")
        poly = self.load_polygon()
        max_count = max(self.LAT_COUNT, self.LON_COUNT)
        
        # Validate input
        if len(base_words) < max_count:
            print(f"Warning: Base word list has {len(base_words)} words, but need {max_count}. Padding with placeholders.")
            # Pad with placeholders if needed
            while len(base_words) < max_count:
                base_words.append(f"word{len(base_words)}")
        
        print(f"Filtering {max_count} coordinate positions against UK/Ireland polygon...")
        results = []
        valid_count = 0
        invalid_count = 0
        
        for i in range(max_count):
            lat = self.LAT_MIN + i * self.STEP if i < self.LAT_COUNT else self.LAT_MIN
            lon = self.LON_MIN + i * self.STEP if i < self.LON_COUNT else self.LON_MIN
            point = Point(lon, lat)
            
            if not poly.contains(point):
                results.append(self.INVALID_POINT)
                invalid_count += 1
            else:
                results.append(base_words[i] if i < len(base_words) else f"word{i}")
                valid_count += 1
        
        # Validate output word list length
        expected_count = max_count
        actual_count = len(results)
        if actual_count != expected_count:
            raise RuntimeError(f"Output word list has {actual_count} entries, expected {expected_count}.")
        
        print(f"Polygon filtering complete: {valid_count} valid positions, {invalid_count} invalid positions")
        
        # Show sample of valid words for verification
        sample_words = [w for w in results[:100] if w != self.INVALID_POINT][:10]
        if sample_words:
            print(f"Sample of first 10 valid words: {sample_words}")
        else:
            print("Warning: No valid words found in first 100 positions")
        
        return results
