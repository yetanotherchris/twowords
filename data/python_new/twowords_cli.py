import os
import argparse
import subprocess
import sys

# When running in container, / is the equivalent of the repo's data folder
if os.path.exists("/python") and os.path.exists("/words"):
    ROOT = "/"
    WORDS_DIR = "/words"
    OUTPUT_DIR = "/output"
    WORDS_TXT = "/output/words.txt"
    WORDS_ZIP = "/expanded_words.zip"  # Root level like old script
else:
    # Get the repo root: data/python_new/twowords_cli.py -> ../../../ -> repo root
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    WORDS_DIR = os.path.join(ROOT, "data", "words")
    OUTPUT_DIR = os.path.join(ROOT, "data", "output")
    WORDS_TXT = os.path.join(OUTPUT_DIR, "words.txt")
    WORDS_ZIP = os.path.join(ROOT, "expanded_words.zip")  # Root level like old script


def show_steps():
    """Show the correct order of steps to run the pipeline."""
    print("TwoWords Data Pipeline - Enhanced with UK Cities Coverage")
    print("=" * 60)
    print()
    print("Run these commands in order:")
    print()
    print("Local Usage:")
    print("1. python twowords_cli.py generate-city-indices")
    print("2. python twowords_cli.py curate-words")
    print("3. python twowords_cli.py verify")
    print()
    print("Docker Usage:")
    print("1. docker run --rm -v $(pwd)/data/output:/output twowords-data generate-city-indices")
    print("2. docker run --rm -v $(pwd)/data/output:/output twowords-data curate-words")
    print("3. docker run --rm -v $(pwd)/data/output:/output twowords-data verify")
    print()
    print("Enhanced Features:")
    print("- City coverage: All 76 UK cities with 2-mile radius coverage")
    print("- Smart word placement: Food dishes at populated areas")
    print("- Enhanced scoring: WordNet integration for better word selection")
    print()
    print("Output files are saved to data/output/ directory.")


def main():
    parser = argparse.ArgumentParser(description="TwoWords CLI Utility - Enhanced Version")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("steps", help="Show the correct order of pipeline steps")
    
    # City indices generation
    city_parser = subparsers.add_parser("generate-city-indices", help="Generate indices for all 76 UK cities with radius coverage")
    city_parser.add_argument("--radius", type=float, default=2.0, help="Radius in miles around each city (default: 2.0)")
    city_parser.add_argument("--verify", action="store_true", help="Verify the generated indices")
    
    # Word curation
    subparsers.add_parser("curate-words", help="Curate and optimize word list with strategic placement")
    subparsers.add_parser("verify", help="Verify mapping correctness")

    args = parser.parse_args()

    if args.command == "steps":
        show_steps()

    elif args.command == "generate-city-indices":
        script_path = os.path.join(os.path.dirname(__file__), "twowords_utils", "cities_best_words_for_center_point.py")
        cmd = [sys.executable, script_path]
        if hasattr(args, 'radius'):
            cmd.extend(["--radius", str(args.radius)])
        if hasattr(args, 'verify') and args.verify:
            cmd.append("--verify")
        subprocess.run(cmd)

    elif args.command == "curate-words":
        # Use the word curation functionality
        from twowords_utils.word_curation import WordCurator
        
        curator = WordCurator(WORDS_DIR)
        optimized_words = curator.curate_words()
        
        # Save to output
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, "words.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in optimized_words:
                f.write(word + '\n')
        
        print(f"Curated word list saved to {output_file}")
        print(f"Total words: {len(optimized_words):,}")

    elif args.command == "verify":
        # Import and run verification
        try:
            from twowords_utils import verify_indices
            script_path = os.path.join(os.path.dirname(__file__), "twowords_utils", "verify_indices.py")
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("Verification script not found. Manual verification:")
                print("1. Check that words.txt has 110,001 lines")
                print("2. Verify no duplicate words")
                print("3. Check that food dishes appear at city indices")
        except ImportError:
            print("Verification module not available. Check output manually.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
