"""
Example usage of the refactored word processing system.
Demonstrates how to use the new modular components following SOLID principles.

Run this script to see the new system in action.
"""

import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twowords_utils.word_list_generator import WordListGenerator
from twowords_utils.word_validator import EnglishWordValidator, StrictEnglishWordValidator, CompositeWordValidator
from twowords_utils.word_loader import WordListFactory
from twowords_utils.word_scorer import WordScorer
from twowords_utils.word_list_optimizer import WordListOptimizer
from twowords_utils.wordnet_analyzer import create_wordnet_analyzer


def main():
    """Demonstrate the new modular word processing system."""
    
    # Assume we're in the twowords_utils directory
    words_dir = os.path.join(os.path.dirname(__file__), '..', 'words')
    
    print("=== TwoWords Refactored Word Processing System ===")
    print(f"Using words directory: {words_dir}")
    print()
    
    # Example 1: Using individual components
    print("1. Using individual components:")
    print("-" * 40)
    
    # Create validators
    basic_validator = EnglishWordValidator()
    strict_validator = StrictEnglishWordValidator()
    composite_validator = CompositeWordValidator([basic_validator, strict_validator])
    
    # Test word validation
    test_words = ['hello', 'world', 'qxz', 'proper_noun', 'test123', 'a', 'pizza']
    print("Testing word validation:")
    for word in test_words:
        basic_valid = basic_validator.is_valid(word)
        strict_valid = strict_validator.is_valid(word)
        composite_valid = composite_validator.is_valid(word)
        print(f"  '{word}': basic={basic_valid}, strict={strict_valid}, composite={composite_valid}")
    print()
    
    # Example 2: Using the word loader factory
    print("2. Using word loader factory:")
    print("-" * 40)
    
    factory = WordListFactory(words_dir)
    
    # Try loading from different sources
    try:
        # Try loading food dishes
        food_loader = factory.create_file_loader('food_dishes_final.txt')
        food_words = food_loader.load_words()
        print(f"Loaded {len(food_words)} food dishes")
        if food_words:
            print(f"  First 5: {food_words[:5]}")
    except Exception as e:
        print(f"  Could not load food dishes: {e}")
    
    try:
        # Try loading from comprehensive sources
        comprehensive_loader = factory.create_comprehensive_loader(max_kaggle_words=1000)
        all_words = comprehensive_loader.load_words()
        print(f"Loaded {len(all_words)} words from comprehensive sources")
        if all_words:
            print(f"  First 5: {all_words[:5]}")
    except Exception as e:
        print(f"  Could not load from comprehensive sources: {e}")
    print()
    
    # Example 3: Using the word scorer
    print("3. Using word scorer:")
    print("-" * 40)
    
    wordnet_analyzer = create_wordnet_analyzer()
    scorer = WordScorer(wordnet_analyzer)
    
    # Score some test words
    test_words_for_scoring = ['pizza', 'cat', 'running', 'happiness', 'xqz', 'the']
    food_dishes = {'pizza', 'pasta', 'bread'}
    common_words = {'cat', 'the', 'happiness'}
    
    print("Scoring test words:")
    for word in test_words_for_scoring:
        score = scorer.calculate_score(word, food_dishes, common_words)
        print(f"  {score}")
    print()
    
    # Example 4: Using the main facade
    print("4. Using the main WordListGenerator facade:")
    print("-" * 40)
    
    generator = WordListGenerator(words_dir)
    
    # Try generating common nouns (if WordNet is available)
    try:
        common_nouns = generator.generate_common_nouns()
        if common_nouns:
            print(f"Generated {len(common_nouns)} common nouns")
            print(f"  First 10: {common_nouns[:10]}")
        else:
            print("No common nouns generated (WordNet may not be available)")
    except Exception as e:
        print(f"  Error generating common nouns: {e}")
    
    print()
    print("=== Refactoring Complete ===")
    print()
    print("The word processing system has been successfully refactored according to SOLID principles:")
    print("- Single Responsibility: Each class has one clear purpose")
    print("- Open/Closed: New validators, loaders, etc. can be added without modifying existing code")
    print("- Liskov Substitution: All validators implement the same interface")
    print("- Interface Segregation: Focused interfaces for different concerns")
    print("- Dependency Inversion: Components depend on abstractions, not concretions")
    print()
    print("For backward compatibility, the old WordPopularity class still works,")
    print("but it now delegates to the new modular system and shows deprecation warnings.")


if __name__ == "__main__":
    main()
