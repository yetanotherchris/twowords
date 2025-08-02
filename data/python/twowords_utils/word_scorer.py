"""
Word scoring utilities for the TwoWords project.
Handles scoring and ranking of words based on various criteria.

Attribution: Scoring algorithms based on TwoWords project requirements
"""

from dataclasses import dataclass
from typing import List, Set
from .wordnet_analyzer import WordNetAnalyzer, create_wordnet_analyzer


@dataclass
class WordScore:
    """Represents a word with its calculated score."""
    word: str
    score: float
    
    def __str__(self) -> str:
        return f"{self.word}: {self.score:.1f}"


class WordScorer:
    """Calculates desirability scores for words."""
    
    def __init__(self, wordnet_analyzer: WordNetAnalyzer = None):
        self.wordnet_analyzer = wordnet_analyzer or create_wordnet_analyzer()
    
    def calculate_score(self, word: str, food_dishes: Set[str] = None, 
                       large_common_words: Set[str] = None) -> WordScore:
        """Calculate a desirability score for a word (higher = better)."""
        
        food_dishes = food_dishes or set()
        large_common_words = large_common_words or set()
        
        length = len(word)
        is_food = word in food_dishes
        is_large_common = word in large_common_words
        is_common = self._is_common_word(word)
        is_simple = self._is_simple_word(word)
        
        # Base score starts higher for shorter words
        score = 100.0
        
        # Length scoring (prefer shorter words)
        score += self._calculate_length_score(length)
        
        # Category bonuses
        if is_food:
            score += 60  # Highest bonus for food dishes
        
        if is_large_common:
            score += 55  # Second highest for large common words
        
        if is_common:
            score += 40  # Legacy common word bonus
        
        if is_simple:
            score += 20  # Simple word bonus
        
        # Single letter handling
        if length == 1 and word not in ['a', 'i']:
            score -= 30
        
        # WordNet-based scoring
        score += self._calculate_wordnet_score(word)
        
        # Grammar-based adjustments
        score += self._calculate_grammar_score(word, is_large_common)
        
        return WordScore(word, score)
    
    def _calculate_length_score(self, length: int) -> float:
        """Calculate score based on word length."""
        if length <= 3:
            return 50  # Very short words get bonus
        elif length <= 4:
            return 40  # Short words get bonus
        elif length <= 5:
            return 20  # Short words get bonus
        elif length <= 7:
            return 0   # Medium words neutral
        elif length <= 10:
            return -20  # Long words get penalty
        else:
            return -50  # Very long words get big penalty
    
    def _calculate_wordnet_score(self, word: str) -> float:
        """Calculate score based on WordNet analysis."""
        score = 0.0
        
        if self.wordnet_analyzer.is_animal(word):
            score += 30
        if self.wordnet_analyzer.is_place(word):
            score += 25
        if self.wordnet_analyzer.is_noun(word):
            score += 20
        if self.wordnet_analyzer.is_adjective(word):
            score += 15
        
        return score
    
    def _calculate_grammar_score(self, word: str, is_large_common: bool) -> float:
        """Calculate score based on grammatical patterns."""
        score = 0.0
        length = len(word)
        
        # Prefer singular nouns over plurals
        if length > 3:
            if word.endswith('ies'):
                score -= 15
            elif word.endswith('es'):
                score -= 10
            elif word.endswith('s'):
                score -= 8
            else:
                score += 8  # Likely singular noun
        
        # Penalize likely verbs
        if word.endswith('ing'):
            score -= 12
        if word.endswith('ed'):
            score -= 8
        
        # Bonus for matching common noun list
        if is_large_common and not word.endswith(('ing', 'ed', 's', 'es', 'ies')):
            score += 10
        
        return score
    
    def _is_common_word(self, word: str) -> bool:
        """Check if word is in basic common words set."""
        common_words = {
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
        return word in common_words
    
    def _is_simple_word(self, word: str) -> bool:
        """Check if word is simple and readable."""
        import re
        if not re.match(r'^[a-z]+$', word):
            return False
        
        difficult_patterns = [
            'qq', 'xx', 'zz', 'uu', 'ii', 'oo',
            'xh', 'xk', 'xj', 'qw', 'qy',
            'ght', 'pht', 'rht',
        ]
        return not any(pattern in word for pattern in difficult_patterns)
    
    def score_words(self, words: List[str], food_dishes: Set[str] = None,
                   large_common_words: Set[str] = None) -> List[WordScore]:
        """Score a list of words and return sorted by score (highest first)."""
        scored_words = []
        
        for word in words:
            score = self.calculate_score(word, food_dishes, large_common_words)
            scored_words.append(score)
        
        # Sort by score (best first)
        scored_words.sort(key=lambda x: x.score, reverse=True)
        
        return scored_words
