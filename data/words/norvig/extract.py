#!/usr/bin/env python3
"""
Script to filter Norvig word list based on length and alphabetic characters.
Filters words to be 3-8 characters long and contain only alphabetic characters.
"""

def filter_word_list(input_file, output_file):
    """
    Filter words from input file and save refined list to output file.
    
    Args:
        input_file (str): Path to input word list file
        output_file (str): Path to output refined word list file
    """
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            words = f.read().splitlines()
        
        print(f"Loaded {len(words):,} words from {input_file}")
        
        # Filter words based on criteria
        filtered_words = []
        for word in words:
            word = word.strip()  # Remove any whitespace
            if (3 <= len(word) <= 8 and word.isalpha()):
                filtered_words.append(word.lower())
        
        # Save filtered words to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in filtered_words:
                f.write(word + '\n')
        
        print(f"Filtered to {len(filtered_words):,} words")
        print(f"Saved refined word list to {output_file}")
        
        # Print some stats
        print(f"\nFiltering removed {len(words) - len(filtered_words):,} words")
        print(f"Retention rate: {len(filtered_words)/len(words)*100:.1f}%")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"Error processing files: {e}")

def main():
    input_file = "norvig-word-list.txt"
    output_file = "norvig-words-filtered.txt"
    
    print("Norvig Word List Filter")
    print("=" * 30)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("Criteria: 3-8 characters, alphabetic only")
    print()
    
    filter_word_list(input_file, output_file)

if __name__ == "__main__":
    main()