"""
Main word list generation facade for the TwoWords project.
Orchestrates word loading, validation, scoring, and optimization.

Attribution: TwoWords project word list generation system
"""

import os
from typing import List, Set
from .word_validator import (
    EnglishWordValidator, StrictEnglishWordValidator, 
    CompositeWordValidator
)
from .word_loader import WordListFactory
from .word_scorer import WordScorer
from .word_list_optimizer import WordListOptimizer
from .wordnet_analyzer import create_wordnet_analyzer

# Constants
WORDS_NEEDED = 110001


class WordListGenerator:
    """
    Facade class that orchestrates the entire word list generation process.
    
    This class follows the Facade pattern to provide a simple interface
    to the complex word processing subsystem.
    """
    
    def __init__(self, words_dir: str):
        """
        Initialize the word list generator.
        
        Args:
            words_dir: Directory containing word source files
        """
        self.words_dir = words_dir
        self.word_factory = WordListFactory(words_dir)
        
        # Initialize components
        self.validator = self._create_validator()
        self.wordnet_analyzer = create_wordnet_analyzer()
        self.scorer = WordScorer(self.wordnet_analyzer)
        self.optimizer = WordListOptimizer(self.scorer)
    
    def _create_validator(self) -> CompositeWordValidator:
        """Create a composite validator for comprehensive word validation."""
        english_validator = EnglishWordValidator()
        strict_validator = StrictEnglishWordValidator()
        
        # Require both basic English and strict validation
        return CompositeWordValidator([english_validator, strict_validator], require_all=True)
    
    def create_popular_words(self) -> List[str]:
        """
        Generate a popular list of words prioritizing food dishes, common nouns, and scoring words.
        
        Returns:
            List of optimized words for the TwoWords mapping
        """
        print("Starting word popularity analysis...")
        
        # Load word sources
        food_dishes = self._load_food_dishes()
        common_words = self._load_common_words()
        base_words = self._load_base_words()
        important_indices = self._load_important_indices()
        
        # Filter words for quality
        filtered_words = self._filter_words(base_words)
        
        print(f"Using {len(filtered_words)} filtered words for optimization")
        
        # Optimize word placement
        optimized_words = self.optimizer.optimize_word_list(
            filtered_words, 
            important_indices, 
            food_dishes, 
            set(common_words),
            WORDS_NEEDED
        )
        
        print(f"Optimized word list with {len(optimized_words)} words")
        return optimized_words
    
    def create_cities_only_words(self) -> List[str]:
        """
        Generate a smaller word list that only covers major UK cities and populated areas.
        
        Returns:
            List of words optimized for city coverage
        """
        print("Starting cities-only word generation...")
        
        # Load high-quality word sources
        food_dishes = self._load_food_dishes()
        common_words = self._load_common_words()
        important_indices = self._load_important_indices()
        
        # Combine and filter quality words
        quality_words = self._get_quality_words(food_dishes, common_words)
        
        return self.optimizer.create_cities_only_list(quality_words, important_indices)
    
    def optimize_word_placement(self, words: List[str]) -> List[str]:
        """
        Optimize placement of pre-filtered words at population centers.
        
        Args:
            words: List of words to optimize
            
        Returns:
            Optimized word list
        """
        food_dishes = self._load_food_dishes()
        common_words = self._load_common_words()
        important_indices = self._load_important_indices()
        
        return self.optimizer.optimize_word_list(
            words,
            important_indices,
            food_dishes,
            set(common_words)
        )
    
    def _load_food_dishes(self) -> List[str]:
        """Load food dishes from file."""
        loader = self.word_factory.create_file_loader('food_dishes_final.txt')
        words = loader.load_words()
        print(f"Loaded {len(words)} food dishes")
        return words
    
    def _load_common_words(self) -> List[str]:
        """Load common words from file."""
        loader = self.word_factory.create_file_loader('common_words.txt')
        words = loader.load_words()
        print(f"Loaded {len(words)} common words")
        return words
    
    def _load_base_words(self) -> List[str]:
        """Load base words from all available sources."""
        # Try expanded words first
        expanded_path = os.path.join(self.words_dir, 'expanded_words.txt')
        if os.path.exists(expanded_path):
            print(f"Loading words from {expanded_path}...")
            loader = self.word_factory.create_file_loader('expanded_words.txt')
            return loader.load_words()
        
        # Fall back to comprehensive loading
        print("Loading words from zip or comprehensive sources...")
        loader = self.word_factory.create_comprehensive_loader(max_kaggle_words=WORDS_NEEDED * 2)
        return loader.load_words()
    
    def _load_important_indices(self) -> Set[int]:
        """Load important indices from file."""
        loader = self.word_factory.create_indices_loader()
        indices = loader.load_indices()
        print(f"Loaded {len(indices)} important indices")
        return indices
    
    def _filter_words(self, words: List[str]) -> List[str]:
        """Filter words using validation rules."""
        filtered = []
        
        for word in words:
            if (2 <= len(word) <= 12 and 
                word.isalpha() and 
                self.validator.is_valid(word)):
                filtered.append(word)
                
            # Stop when we have enough words
            if len(filtered) >= WORDS_NEEDED:
                break
        
        return filtered
    
    def _get_quality_words(self, food_dishes: List[str], common_words: List[str]) -> List[str]:
        """Get high-quality words prioritizing 4-7 character words."""
        quality_words = []
        
        # Add food dishes (prioritized for cities)
        for word in food_dishes:
            if 4 <= len(word) <= 7 and word.isalpha():
                quality_words.append(word)
        
        # Add common words
        for word in common_words:
            if word not in quality_words and 4 <= len(word) <= 7 and word.isalpha():
                quality_words.append(word)
        
        # Load additional words from Kaggle if needed
        try:
            kaggle_loader = self.word_factory.create_kaggle_loader()
            kaggle_words = kaggle_loader.load_words()
            
            for word in kaggle_words:
                if (word not in quality_words and 
                    4 <= len(word) <= 7 and 
                    word.isalpha() and 
                    self.validator.is_valid(word)):
                    quality_words.append(word)
                    
                    # Stop when we have enough quality words
                    if len(quality_words) >= 50000:  # Reasonable limit
                        break
        except Exception as e:
            print(f"Error loading additional words from Kaggle: {e}")
        
        return quality_words
    
    def generate_common_nouns(self) -> List[str]:
        """Generate common nouns dynamically from WordNet and Kaggle data."""
        if not self.wordnet_analyzer.is_available():
            print("WordNet not available for noun generation")
            return []
        
        # Load words from Kaggle
        try:
            kaggle_loader = self.word_factory.create_kaggle_loader(max_words=50000)
            words = kaggle_loader.load_words()
            
            # Use WordNet to identify nouns
            common_nouns = self.wordnet_analyzer.generate_common_nouns(words)
            
            # Write to file
            common_nouns_path = os.path.join(self.words_dir, 'common_nouns.txt')
            with open(common_nouns_path, 'w', encoding='utf-8') as f:
                for noun in sorted(common_nouns):
                    f.write(noun + '\n')
            
            print(f"Generated {len(common_nouns)} common nouns")
            return list(common_nouns)
            
        except Exception as e:
            print(f"Error generating common nouns: {e}")
            return []
