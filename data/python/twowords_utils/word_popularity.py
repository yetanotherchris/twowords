"""
DEPRECATED: This module is being refactored for better adherence to SOLID principles.

Use word_list_generator.WordListGenerator instead for new code.
This module is kept for backward compatibility.

Attribution: TwoWords project word popularity analysis
"""

import warnings
from typing import List, Set
from .word_list_generator import WordListGenerator
from .word_scorer import WordScore

# Re-export for compatibility
WORDS_NEEDED = 110001

# Issue deprecation warning
warnings.warn(
    "WordPopularity class is deprecated. Use WordListGenerator instead.",
    DeprecationWarning,
    stacklevel=2
)


class WordPopularity:
    """
    DEPRECATED: Legacy wrapper around the new modular word processing system.
    
    This class is maintained for backward compatibility but should not be used
    for new code. Use WordListGenerator instead.
    """
    
    def __init__(self, words_dir):
        self.words_dir = words_dir
        self._generator = WordListGenerator(words_dir)
    
    def create_popular_words(self) -> List[str]:
        """DEPRECATED: Use WordListGenerator.create_popular_words() instead."""
        return self._generator.create_popular_words()
    
    def create_cities_only_words(self) -> List[str]:
        """DEPRECATED: Use WordListGenerator.create_cities_only_words() instead."""
        return self._generator.create_cities_only_words()
    
    def optimize_word_placement(self, filtered_words: List[str]) -> List[str]:
        """DEPRECATED: Use WordListGenerator.optimize_word_placement() instead."""
        return self._generator.optimize_word_placement(filtered_words)
    
    def generate_common_nouns(self) -> List[str]:
        """DEPRECATED: Use WordListGenerator.generate_common_nouns() instead."""
        return self._generator.generate_common_nouns()
    
    # Legacy method stubs for backward compatibility
    def is_valid_english_word(self, word: str) -> bool:
        """DEPRECATED: Use word_validator module instead."""
        return self._generator.validator.is_valid(word)
    
    def is_clearly_english_word(self, word: str) -> bool:
        """DEPRECATED: Use word_validator module instead."""
        return self._generator.validator.is_valid(word)
    
    def is_common_word(self, word: str) -> bool:
        """DEPRECATED: Use word_validator module instead."""
        from .word_validator import CommonWordValidator
        validator = CommonWordValidator()
        return validator.is_valid(word)
    
    def is_simple_word(self, word: str) -> bool:
        """DEPRECATED: Use word_validator module instead."""
        from .word_validator import SimpleWordValidator
        validator = SimpleWordValidator()
        return validator.is_valid(word)
    
    def calculate_word_score(self, word: str, food_dishes: Set[str], large_common_words: Set[str] = None) -> WordScore:
        """DEPRECATED: Use word_scorer module instead."""
        return self._generator.scorer.calculate_score(word, food_dishes, large_common_words)
    
    def load_wordlist(self, path: str) -> List[str]:
        """DEPRECATED: Use word_loader module instead."""
        from .word_loader import FileWordLoader
        loader = FileWordLoader(path)
        return loader.load_words()
    
    def load_important_indices(self, file_path: str) -> Set[int]:
        """DEPRECATED: Use word_loader module instead."""
        from .word_loader import IndicesLoader
        loader = IndicesLoader(file_path)
        return loader.load_indices()
    
    def optimize_word_list(self, words: List[str], important_indices: Set[int], 
                          food_dishes: List[str], large_common_words: Set[str] = None) -> List[str]:
        """DEPRECATED: Use word_list_optimizer module instead."""
        return self._generator.optimizer.optimize_word_list(
            words, important_indices, food_dishes, large_common_words
        )
