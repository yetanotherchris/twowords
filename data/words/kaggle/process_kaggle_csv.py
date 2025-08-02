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

Attribution: Processes Kaggle ngram frequency data for TwoWords project
"""

import os
import csv
import zipfile
from typing import List, Set, Dict
from tqdm import tqdm
import wn

def extract_words_from_csv(kaggle_zip_path: str, max_words: int = 200000) -> List[str]:
    """Extract words from the first column of ngram_freq.csv in kaggle.zip."""
    print(f"Extracting first {max_words:,} words from Kaggle CSV...")
    
    if not os.path.exists(kaggle_zip_path):
        raise FileNotFoundError(f"Kaggle zip file not found: {kaggle_zip_path}")
    
    words = []
    try:
        with zipfile.ZipFile(kaggle_zip_path, 'r') as zip_file:
            with zip_file.open('ngram_freq.csv') as csv_file:
                csv_content = csv_file.read().decode('utf-8')
                reader = csv.DictReader(csv_content.splitlines())
                
                for row in reader:
                    word = row['word'].strip().lower()
                    if word and word.isalpha():
                        words.append(word)
                        
                    # Stop when we have enough words
                    if len(words) >= max_words:
                        break
        
        print(f"Extracted {len(words):,} words from CSV")
        return words
        
    except Exception as e:
        raise Exception(f"Error reading CSV from zip: {e}")

def is_valid_english_word(word: str) -> bool:
    """Basic English word validation."""
    if not (3 <= len(word) <= 7):
        return False
    
    if not word.isalpha():
        return False
    
    # Check for bad patterns that don't occur in English
    bad_patterns = ['qq', 'zz', 'xx', 'qx', 'xq', 'kq', 'qk']
    if any(pattern in word for pattern in bad_patterns):
        return False
    
    # Must have at least one vowel (except very short words)
    vowels = 'aeiou'
    if len(word) > 2 and not any(v in word for v in vowels):
        return False
    
    return True

def prefer_singular_forms(words: List[str]) -> List[str]:
    """Prefer singular forms over plurals."""
    word_set = set(words)
    filtered_words = []
    
    print("Processing singular forms...")
    for word in tqdm(words, desc="Singular filter"):
        is_likely_plural = False
        
        # Handle common plural patterns
        if word.endswith('s') and len(word) > 3:
            # Try removing 's'
            candidate = word[:-1]
            if candidate in word_set:
                is_likely_plural = True
            
            # Try 'ies' -> 'y' (e.g., berries -> berry)
            elif word.endswith('ies') and len(word) > 4:
                candidate = word[:-3] + 'y'
                if candidate in word_set:
                    is_likely_plural = True
            
            # Try 'es' -> '' (e.g., boxes -> box)
            elif word.endswith('es') and len(word) > 3:
                candidate = word[:-2]
                if candidate in word_set:
                    is_likely_plural = True
        
        # Only keep the word if it's not a plural
        if not is_likely_plural:
            filtered_words.append(word)
    
    return filtered_words

def remove_prefix_duplicates(words: List[str]) -> List[str]:
    """Remove words that are prefixes of other words."""
    # Use a more efficient approach - sort by length and use set operations
    unique_words = set(words)
    words_to_remove = set()
    
    # Sort words by length for efficient processing
    sorted_words = sorted(unique_words, key=len)
    
    print("Removing prefix duplicates...")
    for i, word in enumerate(tqdm(sorted_words, desc="Prefix removal")):
        if word in words_to_remove:
            continue
            
        # Check if this word is a prefix of any longer word
        for j in range(i + 1, len(sorted_words)):
            longer_word = sorted_words[j]
            if longer_word.startswith(word) and len(longer_word) > len(word):
                words_to_remove.add(word)
                break
    
    # Return words that are not marked for removal
    return [word for word in words if word not in words_to_remove]

def initialize_wordnet():
    """Initialize WordNet database."""
    try:
        # Try to get the English wordnet
        wordnet = wn.Wordnet('oewn:2023')
        return wordnet
    except Exception:
        try:
            print("Downloading WordNet data...")
            wn.download('oewn:2023')
            wordnet = wn.Wordnet('oewn:2023')
            return wordnet
        except Exception as e:
            print(f"Warning: Could not initialize WordNet: {e}")
            return None

def is_animal_wordnet(word: str, wordnet) -> bool:
    """Check if word represents an animal using WordNet."""
    if not wordnet:
        return False
    
    try:
        synsets = wordnet.synsets(word)
        for synset in synsets:
            # Check if any hypernym contains animal-related terms
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    if any(animal_term in lemma.lower() for animal_term in 
                          ['animal', 'mammal', 'bird', 'fish', 'reptile', 'insect']):
                        return True
    except:
        pass
    return False

def is_plant_wordnet(word: str, wordnet) -> bool:
    """Check if word represents a plant using WordNet."""
    if not wordnet:
        return False
    
    try:
        synsets = wordnet.synsets(word)
        for synset in synsets:
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    if any(plant_term in lemma.lower() for plant_term in 
                          ['plant', 'tree', 'flower', 'fruit', 'vegetable', 'herb']):
                        return True
    except:
        pass
    return False

def is_place_wordnet(word: str, wordnet) -> bool:
    """Check if word represents a place using WordNet."""
    if not wordnet:
        return False
    
    try:
        synsets = wordnet.synsets(word)
        for synset in synsets:
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    if any(place_term in lemma.lower() for place_term in 
                          ['place', 'location', 'city', 'country', 'region']):
                        return True
    except:
        pass
    return False

def is_noun_wordnet(word: str, wordnet) -> bool:
    """Check if word is a noun using WordNet."""
    if not wordnet:
        return False
    
    try:
        synsets = wordnet.synsets(word)
        return any(synset.pos == 'n' for synset in synsets)
    except:
        return False

def is_adjective_wordnet(word: str, wordnet) -> bool:
    """Check if word is an adjective using WordNet."""
    if not wordnet:
        return False
    
    try:
        synsets = wordnet.synsets(word)
        return any(synset.pos == 'a' or synset.pos == 's' for synset in synsets)
    except:
        return False
def categorize_words(words: List[str]) -> Dict[str, List[str]]:
    """Categorize words by type using WordNet and fallback patterns."""
    print("Categorizing words by type...")
    
    # Initialize WordNet
    wordnet = initialize_wordnet()
    if wordnet:
        print("Using WordNet for categorization")
    else:
        print("Using fallback pattern matching for categorization")
    
    categories = {
        'animal': [],
        'vegetable': [],  # Plants/food
        'mineral': [],    # Materials/substances
        'place': [],
        'noun': [],
        'adjective': []
    }
    
    # Fallback word lists for when WordNet is not available
    animal_words = {
        'cat', 'dog', 'bird', 'fish', 'bear', 'deer', 'fox', 'wolf', 'lion',
        'tiger', 'cow', 'pig', 'sheep', 'goat', 'horse', 'duck', 'goose',
        'hen', 'rat', 'mouse', 'bat', 'owl', 'hawk', 'eagle', 'swan'
    }
    
    vegetable_words = {
        'apple', 'pear', 'plum', 'grape', 'berry', 'bean', 'pea', 'corn',
        'rice', 'wheat', 'oat', 'rye', 'barley', 'carrot', 'beet', 'onion',
        'garlic', 'herb', 'mint', 'sage', 'basil', 'tree', 'oak', 'pine',
        'elm', 'ash', 'birch', 'maple', 'willow', 'rose', 'lily', 'tulip'
    }
    
    mineral_words = {
        'iron', 'gold', 'silver', 'copper', 'zinc', 'lead', 'tin', 'steel',
        'brass', 'bronze', 'stone', 'rock', 'sand', 'clay', 'coal', 'oil',
        'gas', 'salt', 'lime', 'chalk', 'flint', 'granite', 'marble'
    }
    
    place_words = {
        'city', 'town', 'village', 'hill', 'valley', 'river', 'lake', 'sea',
        'ocean', 'beach', 'coast', 'island', 'mount', 'peak', 'forest',
        'field', 'farm', 'yard', 'garden', 'park', 'road', 'street', 'lane'
    }
    
    adjective_words = {
        'big', 'small', 'large', 'tiny', 'huge', 'long', 'short', 'tall',
        'wide', 'narrow', 'thick', 'thin', 'heavy', 'light', 'strong',
        'weak', 'hard', 'soft', 'rough', 'smooth', 'hot', 'cold', 'warm',
        'cool', 'dry', 'wet', 'clean', 'dirty', 'new', 'old', 'young',
        'fresh', 'stale', 'sweet', 'sour', 'bitter', 'spicy', 'mild',
        'bright', 'dark', 'clear', 'cloudy', 'sharp', 'dull', 'loud',
        'quiet', 'fast', 'slow', 'quick', 'rich', 'poor', 'cheap', 'dear',
        'free', 'busy', 'empty', 'full', 'open', 'closed', 'safe', 'risky'
    }
    
    # Categorize words
    for word in tqdm(words, desc="Categorizing"):
        categorized = False
        
        if wordnet:
            # Try WordNet first
            if is_animal_wordnet(word, wordnet):
                categories['animal'].append(word)
                categorized = True
            elif is_plant_wordnet(word, wordnet):
                categories['vegetable'].append(word)
                categorized = True
            elif is_place_wordnet(word, wordnet):
                categories['place'].append(word)
                categorized = True
            elif is_adjective_wordnet(word, wordnet):
                categories['adjective'].append(word)
                categorized = True
            elif is_noun_wordnet(word, wordnet):
                categories['noun'].append(word)
                categorized = True
        
        # Fallback to pattern matching if WordNet didn't categorize it
        if not categorized:
            if word in animal_words:
                categories['animal'].append(word)
            elif word in vegetable_words:
                categories['vegetable'].append(word)
            elif word in mineral_words:
                categories['mineral'].append(word)
            elif word in place_words:
                categories['place'].append(word)
            elif word in adjective_words:
                categories['adjective'].append(word)
            else:
                categories['noun'].append(word)
    
    # Print category statistics
    for category, word_list in categories.items():
        print(f"  {category}: {len(word_list):,} words")
    
    return categories

def main():
    """Main processing function."""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kaggle_zip = os.path.join(script_dir, "kaggle.zip")
    output_dir = script_dir
    
    print("Kaggle CSV Word Processor")
    print("=" * 40)
    print(f"Input: {kaggle_zip}")
    print(f"Output: {output_dir}")
    print()
    
    if not os.path.exists(kaggle_zip):
        print(f"Error: Kaggle zip file not found at {kaggle_zip}")
        print("Please ensure the kaggle.zip file exists in this directory.")
        return False
    
    try:
        # Step 1: Extract words from CSV
        print("Step 1: Extracting words from CSV...")
        raw_words = extract_words_from_csv(kaggle_zip)
        
        # Step 2: Filter by length and validation
        print("Step 2: Filtering words by length and validation...")
        length_filtered = []
        for word in tqdm(raw_words, desc="Length filter"):
            if is_valid_english_word(word):
                length_filtered.append(word)
        
        print(f"After length/validation filter: {len(length_filtered):,} words")
        
        # Step 3: Remove duplicates and sort
        unique_words = list(set(length_filtered))
        print(f"After removing duplicates: {len(unique_words):,} words")
        
        # Step 4: Prefer singular forms
        print("Step 3: Preferring singular forms...")
        singular_preferred = prefer_singular_forms(unique_words)
        print(f"After singular preference: {len(singular_preferred):,} words")
        
        # Step 5: Remove prefix duplicates
        print("Step 4: Removing prefix duplicates...")
        no_prefix_duplicates = remove_prefix_duplicates(singular_preferred)
        print(f"After removing prefix duplicates: {len(no_prefix_duplicates):,} words")
        
        # Step 6: Write initial words file
        initial_file = os.path.join(output_dir, "initial_words.txt")
        with open(initial_file, 'w', encoding='utf-8') as f:
            for word in sorted(no_prefix_duplicates):
                f.write(f"{word}\n")
        
        print(f"Written {len(no_prefix_duplicates):,} words to {initial_file}")
        
        # Step 7: Categorize words
        print("Step 5: Categorizing words...")
        categories = categorize_words(no_prefix_duplicates)
        
        # Step 8: Write refined words file
        refined_file = os.path.join(output_dir, "refined_words.txt")
        with open(refined_file, 'w', encoding='utf-8') as f:
            for category, word_list in categories.items():
                if word_list:  # Only write non-empty categories
                    for word in sorted(word_list):
                        f.write(f"{word}\n")
        
        total_words = sum(len(word_list) for word_list in categories.values())
        print(f"Written {total_words:,} categorized words to {refined_file}")
        
        print("\n✓ SUCCESS: Kaggle CSV processing completed!")
        print(f"Initial words: {initial_file}")
        print(f"Refined words: {refined_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
