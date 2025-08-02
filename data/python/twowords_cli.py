import os
import argparse
from twowords_utils.polygon_utils import PolygonUtils
from twowords_utils.word_popularity import WordPopularity
from twowords_utils.zip_utils import ZipUtils

# When running in container, / is the equivalent of the repo's data folder
if os.path.exists("/python") and os.path.exists("/words"):
    ROOT = "/"
    WORDS_DIR = "/words"
    OUTPUT_DIR = "/output"
    WORDS_TXT = "/output/words.txt"
    WORDS_ZIP = "/words.zip"  # Root level like old script
else:
    # Get the repo root: data/python/twowords_cli.py -> ../../ -> repo root
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    WORDS_DIR = os.path.join(ROOT, "data", "words")
    OUTPUT_DIR = os.path.join(ROOT, "data", "output")
    WORDS_TXT = os.path.join(OUTPUT_DIR, "words.txt")
    WORDS_ZIP = os.path.join(ROOT, "words.zip")  # Root level like old script


def generate_popular_list(cities_only=False):
    popularity = WordPopularity(WORDS_DIR)
    
    if cities_only:
        words = popularity.create_cities_only_words()
        print(f"Cities-only word list written to {WORDS_TXT}")
    else:
        words = popularity.create_popular_words()
        print(f"Popular word list written to {WORDS_TXT}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(WORDS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(words))


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


def show_steps():
    """Show the correct order of steps to run the pipeline."""
    print("TwoWords Data Pipeline - Correct Order of Steps")
    print("=" * 50)
    print()
    print("Run these commands in order:")
    print()
    print("Local Usage:")
    print("1. python twowords_cli.py download-polygon")
    print("2. python twowords_cli.py popular [--cities-only]")
    print("3. python twowords_cli.py filter")
    print("4. python twowords_cli.py calculate-indices")
    print("5. python twowords_cli.py optimize")
    print("6. python twowords_cli.py shuffle")
    print("7. python twowords_cli.py verify")
    print("8. python twowords_cli.py zip")
    print()
    print("Docker Usage:")
    print("1. docker run --rm -v $(pwd)/data/output:/output twowords-data download-polygon")
    print("2. docker run --rm -v $(pwd)/data/output:/output twowords-data popular [--cities-only]")
    print("3. docker run --rm -v $(pwd)/data/output:/output twowords-data filter")
    print("4. docker run --rm -v $(pwd)/data/output:/output twowords-data calculate-indices")
    print("5. docker run --rm -v $(pwd)/data/output:/output twowords-data optimize")
    print("6. docker run --rm -v $(pwd)/data/output:/output twowords-data shuffle")
    print("7. docker run --rm -v $(pwd)/data/output:/output twowords-data verify")
    print("8. docker run --rm -v $(pwd)/data/output:/output twowords-data zip")
    print()
    print("Each step depends on the previous ones. Run them in this exact order.")
    print("Output files are saved to data/output/ directory.")


def main():
    parser = argparse.ArgumentParser(description="TwoWords CLI Utility")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("steps", help="Show the correct order of pipeline steps")
    popular_parser = subparsers.add_parser("popular", help="Generate popular list of words")
    popular_parser.add_argument("--cities-only", action="store_true", help="Only fill indices for major cities (faster, smaller output)")
    subparsers.add_parser("filter", help="Filter words for polygon (mark out-of-bounds indices)")
    subparsers.add_parser("optimize", help="Optimize word list placing best words at population centers")
    subparsers.add_parser("shuffle", help="Shuffle words to prevent alphabetical clustering while preserving polygon filtering")
    subparsers.add_parser("calculate-indices", help="Calculate indices for major UK cities")
    subparsers.add_parser("verify", help="Verify mapping correctness")
    subparsers.add_parser("zip", help="Generate words.zip from output/words.txt")
    subparsers.add_parser("download-polygon", help="Download or refresh the polygon zip file")

    args = parser.parse_args()

    if args.command == "steps":
        show_steps()

    elif args.command == "popular":
        generate_popular_list(cities_only=args.cities_only)

    elif args.command == "filter":
        PolygonUtils(ROOT).ensure_polygon()
        filter_words_for_polygon()

    elif args.command == "optimize":
        import sys
        import os
        # Add the parent directory to the path so twowords_utils can be imported
        sys.path.insert(0, os.path.dirname(__file__))
        # Temporarily clear command line arguments to avoid conflicts
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0]]  # Keep only the script name
        try:
            from twowords_utils.optimize_word_list import optimize_words
            optimize_words()
        finally:
            sys.argv = original_argv

    elif args.command == "calculate-indices":
        import sys
        import os
        # Add the parent directory to the path so twowords_utils can be imported
        sys.path.insert(0, os.path.dirname(__file__))
        # Temporarily clear command line arguments to avoid conflicts
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0]]  # Keep only the script name
        try:
            from twowords_utils.calculate_popular_indices import main as calc_main
            calc_main()
        finally:
            sys.argv = original_argv

    elif args.command == "shuffle":
        import subprocess
        import sys
        import os
        script_path = os.path.join(os.path.dirname(__file__), "twowords_utils", "shuffle_words.py")
        subprocess.run([sys.executable, script_path])

    elif args.command == "verify":
        import sys
        import os
        # Add the parent directory to the path so twowords_utils can be imported
        sys.path.insert(0, os.path.dirname(__file__))
        # Temporarily clear command line arguments to avoid conflicts
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0]]  # Keep only the script name
        try:
            from twowords_utils.verify_indices import main as verify_main
            verify_main()
        finally:
            sys.argv = original_argv

    elif args.command == "zip":
        generate_zip()

    elif args.command == "download-polygon":
        PolygonUtils(ROOT).download_polygon()
        print("Downloaded UK polygon to /polygons/uk_polygon.wkt.zip")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
