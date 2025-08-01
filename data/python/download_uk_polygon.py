import sys
sys.path.insert(0, '../')
from generate_word_list import download_polygon

if __name__ == "__main__":
    download_polygon()
    print("Downloaded UK polygon to data/polygons/uk_polygon.wkt.zip")
