"""
Word validation utilities for the TwoWords project.
Handles validation of English words according to project-specific criteria.

Attribution: Based on analysis of word patterns and English language rules.
"""

import re
from typing import Set
from abc import ABC, abstractmethod


class WordValidator(ABC):
    """Abstract base class for word validation."""
    
    @abstractmethod
    def is_valid(self, word: str) -> bool:
        """Check if a word is valid according to the validator's criteria."""
        pass


class EnglishWordValidator(WordValidator):
    """Validates words based on English language patterns and rules."""
    
    def __init__(self):
        self.bad_patterns = [
            'qq', 'zz', 'xx', 'bv', 'cj', 'cv', 'cw', 'dx', 'fq', 'fx', 'gq', 'gx', 'hx',
            'jf', 'jg', 'jq', 'jv', 'jw', 'jx', 'jz', 'kq', 'kx', 'mx', 'px', 'qc', 'qf',
            'qg', 'qh', 'qj', 'qk', 'ql', 'qm', 'qn', 'qp', 'qr', 'qs', 'qt', 'qv', 'qw',
            'qx', 'qy', 'qz', 'sx', 'vb', 'vf', 'vh', 'vj', 'vm', 'vp', 'vq', 'vt', 'vw',
            'vx', 'wq', 'wx', 'xf', 'xj', 'xk', 'xm', 'xp', 'xq', 'xv', 'xw', 'xz', 'zx'
        ]
        
        self.valid_endings = 'aeiouynslrdtmh'
        self.vowels = 'aeiou'
    
    def is_valid(self, word: str) -> bool:
        """Check if a word follows basic English patterns."""
        return (
            self._has_valid_length(word) and
            self._has_vowels(word) and
            self._has_valid_consonant_clusters(word) and
            self._has_valid_patterns(word) and
            self._has_valid_case(word) and
            self._has_valid_ending(word)
        )
    
    def _has_valid_length(self, word: str) -> bool:
        """Check if word length is reasonable."""
        return 1 <= len(word) <= 12
    
    def _has_vowels(self, word: str) -> bool:
        """Check if word has vowels (except very short words)."""
        if len(word) > 2:
            return any(c in word for c in self.vowels)
        return True
    
    def _has_valid_consonant_clusters(self, word: str) -> bool:
        """Check for excessive consonant clusters."""
        consonant_count = 0
        for char in word:
            if char not in self.vowels:
                consonant_count += 1
                if consonant_count > 3:
                    return False
            else:
                consonant_count = 0
        return True
    
    def _has_valid_patterns(self, word: str) -> bool:
        """Check for invalid letter combinations."""
        return not any(pattern in word for pattern in self.bad_patterns)
    
    def _has_valid_case(self, word: str) -> bool:
        """Check for valid capitalization patterns."""
        if len(word) <= 4 and word.isupper():
            return False
        if len(word) <= 3 and any(char.isupper() for char in word):
            return False
        return True
    
    def _has_valid_ending(self, word: str) -> bool:
        """Check if word has a reasonable ending."""
        if len(word) == 1:
            return word in ['a', 'i']
        if len(word) > 3:
            return word[-1] in self.valid_endings
        return True


class StrictEnglishWordValidator(EnglishWordValidator):
    """More strict validation for clearly English words."""
    
    def __init__(self):
        super().__init__()
        self.consonant_clusters = [
            'bcf', 'bch', 'bdl', 'bdr', 'bgl', 'bkc', 'bkg', 'bkl', 'bkp', 'bkt',
            'cpt', 'ctn', 'ctx', 'cwt', 'dbl', 'dft', 'dgr', 'dpt', 'dvt', 'frt',
            'gln', 'grd', 'hwy', 'inc', 'ltd', 'mfg', 'mgr', 'pkg', 'pkt', 'plt',
            'pnt', 'qty', 'rpt', 'sgt', 'spl', 'std', 'str', 'tbl', 'tmp', 'wgt'
        ]
    
    def is_valid(self, word: str) -> bool:
        """Apply strict validation for clearly English words."""
        return (
            super().is_valid(word) and
            self._has_valid_vowel_ratio(word) and
            not self._has_proper_noun_case(word) and
            not self._has_repeated_vowels(word) and
            not self._has_abbreviation_patterns(word)
        )
    
    def _has_valid_vowel_ratio(self, word: str) -> bool:
        """Check if vowel ratio is reasonable for English."""
        vowels = sum(1 for c in word if c in self.vowels)
        if len(word) > 3 and vowels == 0:
            return False
        
        vowel_ratio = vowels / len(word)
        return 0.2 <= vowel_ratio <= 0.7
    
    def _has_proper_noun_case(self, word: str) -> bool:
        """Check if word looks like a proper noun."""
        return word[0].isupper()
    
    def _has_repeated_vowels(self, word: str) -> bool:
        """Check for excessive repeated vowels."""
        return any(pattern * 2 in word for pattern in ['aa', 'ii', 'oo', 'uu'])
    
    def _has_abbreviation_patterns(self, word: str) -> bool:
        """Check for abbreviation-like patterns."""
        return any(cluster in word for cluster in self.consonant_clusters)


class SimpleWordValidator(WordValidator):
    """Validates words for simplicity and readability."""
    
    def __init__(self):
        self.difficult_patterns = [
            'qq', 'xx', 'zz', 'uu', 'ii', 'oo',
            'xh', 'xk', 'xj', 'qw', 'qy',
            'ght', 'pht', 'rht'
        ]
    
    def is_valid(self, word: str) -> bool:
        """Check if word is simple and readable."""
        return (
            re.match(r'^[a-z]+$', word) and
            not any(pattern in word for pattern in self.difficult_patterns)
        )


class CommonWordValidator(WordValidator):
    """Validates words against a set of common English words."""
    
    def __init__(self):
        self.common_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'have', 'had', 'this',
            'but', 'his', 'her', 'she', 'or', 'if', 'we', 'my', 'me', 'all',
            'up', 'out', 'so', 'can', 'get', 'go', 'new', 'now', 'old', 'see',
            'two', 'way', 'who', 'boy', 'did', 'let', 'put', 'say',
            'too', 'use', 'big', 'car', 'cat', 'dog', 'eye', 'far',
            'few', 'got', 'him', 'how', 'man', 'may', 'not', 'oil',
            'one', 'our', 'own', 'run', 'sun', 'top', 'try', 'yet', 'yes',
            'day', 'end', 'way', 'any', 'may', 'say', 'new', 'old', 'see',
            'him', 'two', 'how', 'its', 'who', 'oil', 'sit', 'set', 'hot',
            'lot', 'cut', 'put', 'but', 'got', 'not', 'out', 'our', 'now',
            'low', 'few', 'new', 'too', 'you', 'use', 'run', 'sun', 'fun',
            'red', 'bed', 'led', 'fed', 'had', 'bad', 'mad', 'sad', 'dad',
            'add', 'all', 'call', 'ball', 'fall', 'wall', 'tall', 'small',
            'home', 'come', 'some', 'time', 'name', 'same', 'game', 'came',
            'take', 'make', 'wake', 'lake', 'cake', 'bake', 'sake', 'fake',
            'like', 'bike', 'hike', 'mike', 'pike', 'life', 'wife', 'nice',
            'rice', 'mice', 'dice', 'ice', 'face', 'race', 'pace', 'lace',
            'place', 'space', 'grace', 'trace', 'brace', 'fire', 'tire',
            'wire', 'hire', 'dire', 'mire', 'sure', 'pure', 'cure', 'lure',
            'blue', 'true', 'clue', 'glue', 'due', 'sue', 'hue', 'cue',
            'side', 'ride', 'hide', 'wide', 'tide', 'bride', 'pride', 'slide',
            'house', 'mouse', 'about', 'water', 'after', 'first', 'never',
            'other', 'right', 'think', 'where', 'being', 'every', 'great',
            'might', 'still', 'small', 'found', 'those', 'never', 'under',
            'while', 'again', 'place', 'right', 'three', 'state', 'after',
            'good', 'well', 'much', 'very', 'when', 'here', 'work', 'year',
            'back', 'down', 'over', 'also', 'just', 'only', 'know', 'take',
            'look', 'give', 'most', 'hand', 'high', 'part', 'head', 'keep',
            'help', 'turn', 'move', 'live', 'seem', 'feel', 'want', 'need',
            'find', 'tell', 'such', 'long', 'next', 'last', 'left', 'each',
            'both', 'many', 'more', 'than', 'same', 'them', 'what', 'does'
        }
    
    def is_valid(self, word: str) -> bool:
        """Check if word is in the common words set."""
        return word in self.common_words


class CompositeWordValidator(WordValidator):
    """Combines multiple validators using logical operations."""
    
    def __init__(self, validators: list[WordValidator], require_all: bool = True):
        """
        Initialize composite validator.
        
        Args:
            validators: List of validators to combine
            require_all: If True, all validators must pass. If False, any validator can pass.
        """
        self.validators = validators
        self.require_all = require_all
    
    def is_valid(self, word: str) -> bool:
        """Check word against all validators."""
        if self.require_all:
            return all(validator.is_valid(word) for validator in self.validators)
        else:
            return any(validator.is_valid(word) for validator in self.validators)
