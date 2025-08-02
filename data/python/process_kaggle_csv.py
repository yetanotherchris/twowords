#!/usr/bin/env python3
"""
Process Kaggle CSV to create refined word lists.

This script processes the kaggle.zip/ngram_freq.csv file and:
1. Converts CSV to text file, taking the first column (words)
2. Filters for 3-7 character words, prefers singular over plural, 
   removes words that start with existing words (e.g. "find" and "finding")
3. Writes initial_words.txt
4. Further filters by word type (animal, vegetable, mineral, place, noun, adjective)
5. Writes refined_words.txt

Attribution: Uses existing TwoWords project utilities and patterns
"""

import os
import csv
import zipfile
import re
from typing import List, Set, Dict
from collections import defaultdict

# Import existing utilities
from twowords_utils.word_validator import EnglishWordValidator, StrictEnglishWordValidator
from twowords_utils.wordnet_analyzer import create_wordnet_analyzer


class KaggleProcessor:
    """Processes Kaggle CSV data for the TwoWords project."""
    
    def __init__(self, csv_path: str, output_dir: str):
        """
        Initialize the processor.
        
        Args:
            csv_path: Path to kaggle.zip file containing ngram_freq.csv
            output_dir: Directory to write output files
        """
        self.csv_path = csv_path
        self.output_dir = output_dir
        
        # Initialize validators and analyzers
        self.english_validator = EnglishWordValidator()
        self.strict_validator = StrictEnglishWordValidator()
        self.wordnet_analyzer = create_wordnet_analyzer()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_words_from_csv(self) -> List[str]:
        """
        Extract words from the first column of ngram_freq.csv in kaggle.zip.
        
        Returns:
            List of words from the CSV file
        """
        print("Extracting words from Kaggle CSV...")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Kaggle zip file not found: {self.csv_path}")
        
        words = []
        try:
            with zipfile.ZipFile(self.csv_path, 'r') as zip_file:
                with zip_file.open('ngram_freq.csv') as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                    reader = csv.DictReader(csv_content.splitlines())
                    
                    for row in reader:
                        word = row['word'].strip().lower()
                        if word and word.isalpha():
                            words.append(word)
            
            print(f"Extracted {len(words):,} words from CSV")
            return words
            
        except Exception as e:
            raise Exception(f"Error reading CSV from zip: {e}")
    
    def filter_initial_words(self, words: List[str]) -> List[str]:
        """
        Filter words for initial list:
        - 3-7 character words only
        - Prefer singular over plural forms
        - Remove words that start with existing words (e.g. "find"/"finding")
        - Basic English validation
        
        Args:
            words: Input word list
            
        Returns:
            Filtered word list
        """
        print("Filtering words for initial list...")
        
        # Step 1: Filter by length and basic validation
        length_filtered = []
        for word in words:
            if (3 <= len(word) <= 7 and 
                word.isalpha() and 
                self.english_validator.is_valid(word)):
                length_filtered.append(word)
        
        print(f"After length/validation filter: {len(length_filtered):,} words")
        
        # Step 2: Handle plurals - prefer singular forms
        singular_preferred = self._prefer_singular_forms(length_filtered)
        print(f"After singular preference: {len(singular_preferred):,} words")
        
        # Step 3: Remove words that are prefixes of other words
        no_prefix_duplicates = self._remove_prefix_duplicates(singular_preferred)
        print(f"After removing prefix duplicates: {len(no_prefix_duplicates):,} words")
        
        return no_prefix_duplicates
    
    def _prefer_singular_forms(self, words: List[str]) -> List[str]:
        """
        Prefer singular forms over plurals.
        
        Args:
            words: Input word list
            
        Returns:
            List with plurals removed where singular exists
        """
        word_set = set(words)
        filtered_words = []
        
        for word in words:
            # Check if this might be a plural
            is_likely_plural = False
            singular_candidate = None
            
            # Handle common plural patterns
            if word.endswith('s') and len(word) > 3:
                # Try removing 's'
                candidate = word[:-1]
                if candidate in word_set:
                    is_likely_plural = True
                    singular_candidate = candidate
                
                # Try 'ies' -> 'y' (e.g., berries -> berry)
                if word.endswith('ies') and len(word) > 4:
                    candidate = word[:-3] + 'y'
                    if candidate in word_set:
                        is_likely_plural = True
                        singular_candidate = candidate
                
                # Try 'es' -> '' (e.g., boxes -> box)
                if word.endswith('es') and len(word) > 3:
                    candidate = word[:-2]
                    if candidate in word_set:
                        is_likely_plural = True
                        singular_candidate = candidate
            
            # Only keep the word if it's not a plural or if singular doesn't exist
            if not is_likely_plural:
                filtered_words.append(word)
        
        return filtered_words
    
    def _remove_prefix_duplicates(self, words: List[str]) -> List[str]:
        """
        Remove words that are prefixes of other words.
        E.g., if both "find" and "finding" exist, keep only "find".
        
        Args:
            words: Input word list
            
        Returns:
            List with prefix duplicates removed
        """
        word_set = set(words)
        filtered_words = []
        
        for word in words:
            # Check if this word is a prefix of any other word
            is_prefix = False
            
            for other_word in word_set:
                if (other_word != word and 
                    other_word.startswith(word) and 
                    len(other_word) > len(word)):
                    # This word is a prefix of another word
                    is_prefix = True
                    break
            
            # Only keep the word if it's not a prefix of another word
            if not is_prefix:
                filtered_words.append(word)
        
        return filtered_words
    
    def categorize_words(self, words: List[str]) -> Dict[str, List[str]]:
        """
        Categorize words by type: animal, vegetable, mineral, place, noun, adjective.
        
        Args:
            words: Input word list
            
        Returns:
            Dictionary mapping categories to word lists
        """
        print("Categorizing words by type...")
        
        categories = {
            'animal': [],
            'vegetable': [],  # Plants/food
            'mineral': [],    # Materials/substances
            'place': [],
            'noun': [],
            'adjective': []
        }
        
        # Define some basic pattern matching for categories
        vegetable_indicators = {
            'food', 'fruit', 'berry', 'bean', 'pea', 'corn', 'rice', 'wheat',
            'apple', 'orange', 'grape', 'banana', 'cherry', 'peach', 'pear',
            'carrot', 'potato', 'tomato', 'onion', 'garlic', 'herb', 'spice',
            'plant', 'tree', 'flower', 'leaf', 'root', 'seed', 'grain'
        }
        
        mineral_indicators = {
            'metal', 'iron', 'gold', 'silver', 'copper', 'zinc', 'stone',
            'rock', 'crystal', 'diamond', 'coal', 'oil', 'gas', 'steel',
            'aluminum', 'bronze', 'brass', 'lead', 'tin', 'mineral'
        }
        
        # Use WordNet for more sophisticated classification
        if self.wordnet_analyzer and self.wordnet_analyzer.is_available():
            for word in words:
                try:
                    # Check specific categories using WordNet
                    if self.wordnet_analyzer.is_animal(word):
                        categories['animal'].append(word)
                    elif self.wordnet_analyzer.is_place(word):
                        categories['place'].append(word)
                    elif self.wordnet_analyzer.is_noun(word):
                        # Further categorize nouns
                        if any(indicator in word for indicator in vegetable_indicators):
                            categories['vegetable'].append(word)
                        elif any(indicator in word for indicator in mineral_indicators):
                            categories['mineral'].append(word)
                        else:
                            categories['noun'].append(word)
                    elif self.wordnet_analyzer.is_adjective(word):
                        categories['adjective'].append(word)
                    else:
                        # Default to noun if we can't categorize
                        categories['noun'].append(word)
                        
                except Exception:
                    # If WordNet analysis fails, use basic pattern matching
                    categories['noun'].append(word)
        else:
            # Fallback to basic pattern matching if WordNet is not available
            print("WordNet not available, using basic pattern matching...")
            for word in words:
                if any(indicator in word for indicator in vegetable_indicators):
                    categories['vegetable'].append(word)
                elif any(indicator in word for indicator in mineral_indicators):
                    categories['mineral'].append(word)
                else:
                    categories['noun'].append(word)
        
        # Print category statistics
        for category, word_list in categories.items():
            print(f"  {category}: {len(word_list):,} words")
        
        return categories
    
    def write_initial_words(self, words: List[str]) -> str:
        """
        Write initial filtered words to initial_words.txt.
        
        Args:
            words: Filtered word list
            
        Returns:
            Path to output file
        """
        output_file = os.path.join(self.output_dir, "initial_words.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(words):
                f.write(f"{word}\n")
        
        print(f"Written {len(words):,} words to {output_file}")
        return output_file
    
    def write_refined_words(self, categories: Dict[str, List[str]]) -> str:
        """
        Write categorized words to refined_words.txt.
        
        Args:
            categories: Dictionary of categorized words
            
        Returns:
            Path to output file
        """
        output_file = os.path.join(self.output_dir, "refined_words.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Refined word list categorized by type\n")
            f.write("# Attribution: Processed from Kaggle ngram frequency data\n\n")
            
            for category, word_list in categories.items():
                if word_list:  # Only write non-empty categories
                    f.write(f"# {category.upper()} ({len(word_list)} words)\n")
                    for word in sorted(word_list):
                        f.write(f"{word}\n")
                    f.write("\n")
        
        total_words = sum(len(word_list) for word_list in categories.values())
        print(f"Written {total_words:,} categorized words to {output_file}")
        return output_file
    
    def process(self) -> tuple[str, str]:
        """
        Run the complete processing pipeline.
        
        Returns:
            Tuple of (initial_words_file, refined_words_file) paths
        """
        print("Starting Kaggle CSV processing pipeline...")
        print("=" * 60)
        
        # Step 1: Extract words from CSV
        raw_words = self.extract_words_from_csv()
        
        # Step 2: Filter for initial word list
        initial_words = self.filter_initial_words(raw_words)
        
        # Step 3: Write initial words
        initial_file = self.write_initial_words(initial_words)
        
        # Step 4: Categorize words
        categories = self.categorize_words(initial_words)
        
        # Step 5: Write refined words
        refined_file = self.write_refined_words(categories)
        
        print("=" * 60)
        print("Processing complete!")
        print(f"Initial words: {initial_file}")
        print(f"Refined words: {refined_file}")
        
        return initial_file, refined_file


def main():
    """Main entry point for the script."""
    # Determine paths based on environment
    if os.path.exists("/python") and os.path.exists("/sources"):
        # Running in container
        kaggle_zip = "/sources/kaggle/kaggle.zip"
        output_dir = "/output"
    else:
        # Running locally
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        kaggle_zip = os.path.join(repo_root, "data", "sources", "kaggle", "kaggle.zip")
        output_dir = os.path.join(repo_root, "data", "output")
    
    print("Kaggle CSV Word Processor")
    print("=" * 40)
    print(f"Input: {kaggle_zip}")
    print(f"Output: {output_dir}")
    print()
    
    if not os.path.exists(kaggle_zip):
        print(f"Error: Kaggle zip file not found at {kaggle_zip}")
        print("Please ensure the kaggle.zip file exists in the correct location.")
        return False
    
    try:
        processor = KaggleProcessor(kaggle_zip, output_dir)
        initial_file, refined_file = processor.process()
        
        print("\n✓ SUCCESS: Kaggle CSV processing completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
