import os
import zipfile
from shapely import wkt
from shapely.geometry import LineString

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
WORD_FILE = os.path.join(ROOT, "word-data", "norvig-word-list.txt")
POLY_WKT = os.path.join(ROOT, "word-data", "uk_polygon.wkt")
OUTPUT_ZIP = os.path.join(ROOT, "expanded_words.zip")


def load_polygon():
    with open(POLY_WKT, "r", encoding="utf-8") as f:
        data = f.read()
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
