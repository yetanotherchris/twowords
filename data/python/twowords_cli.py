import os
import argparse
from twowords_utils.polygon_utils import PolygonUtils
from twowords_utils.word_curation import WordCurator
from twowords_utils.zip_utils import ZipUtils

# When running in container, / is the equivalent of the repo's data folder
if os.path.exists("/python") and os.path.exists("/words"):
    ROOT = "/"
    WORDS_DIR = "/words"
    OUTPUT_DIR = "/output"
    WORDS_TXT = "/output/words.txt"
    WORDS_ZIP = "/words.zip"
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WORDS_DIR = os.path.join(ROOT, "data", "words")
    OUTPUT_DIR = os.path.join(ROOT, "data", "output")
    WORDS_TXT = os.path.join(OUTPUT_DIR, "words.txt")
    WORDS_ZIP = os.path.join(ROOT, "words.zip")


def generate_curated_list():
    curator = WordCurator(WORDS_DIR)
    words = curator.curate_words()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(WORDS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(words))

    print(f"Curated word list written to {WORDS_TXT}")


def filter_words_for_polygon():
    polygon_utils = PolygonUtils(ROOT)
    polygon_utils.validate_polygon_zip()

    with open(WORDS_TXT, "r", encoding="utf-8") as f:
        base_words = [line.strip() for line in f if line.strip()]

    filtered_words = polygon_utils.filter_words_for_polygon(base_words)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(WORDS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_words))

    print(f"Filtered word list written to {WORDS_TXT}")


def generate_zip():
    ZipUtils.create_words_zip(WORDS_TXT, WORDS_ZIP)
    print(f"Created zip file: {WORDS_ZIP}")


def main():
    parser = argparse.ArgumentParser(description="TwoWords CLI Utility")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("curate", help="Generate curated list of words")
    subparsers.add_parser("filter", help="Filter words for polygon (mark out-of-bounds indices)")
    subparsers.add_parser("zip", help="Generate words.zip from output/words.txt")
    subparsers.add_parser("download-polygon", help="Download or refresh the polygon zip file")

    args = parser.parse_args()

    if args.command == "curate":
        generate_curated_list()

    elif args.command == "filter":
        PolygonUtils(ROOT).ensure_polygon()
        filter_words_for_polygon()

    elif args.command == "zip":
        generate_zip()

    elif args.command == "download-polygon":
        PolygonUtils(ROOT).download_polygon()
        print("Downloaded UK polygon to /polygons/uk_polygon.wkt.zip")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
