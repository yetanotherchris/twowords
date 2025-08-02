"""
WordNet analysis utilities for the TwoWords project.
Provides semantic analysis of words using WordNet data.

Attribution: WordNet data from Open English WordNet (OEWN)
"""

from typing import List, Set
from abc import ABC, abstractmethod


class WordNetAnalyzer(ABC):
    """Abstract base class for WordNet analysis."""
    
    @abstractmethod
    def is_animal(self, word: str) -> bool:
        """Check if word represents an animal."""
        pass
    
    @abstractmethod
    def is_place(self, word: str) -> bool:
        """Check if word represents a place."""
        pass
    
    @abstractmethod
    def is_noun(self, word: str) -> bool:
        """Check if word is a noun."""
        pass
    
    @abstractmethod
    def is_adjective(self, word: str) -> bool:
        """Check if word is an adjective."""
        pass


class OpenWordNetAnalyzer(WordNetAnalyzer):
    """WordNet analyzer using the wn library."""
    
    def __init__(self):
        self.wn_en = None
        self._initialize_wordnet()
    
    def _initialize_wordnet(self):
        """Initialize WordNet with error handling."""
        try:
            import wn
            try:
                self.wn_en = wn.Wordnet('oewn:2023')
            except Exception:
                print("Downloading WordNet data...")
                wn.download('oewn:2023')
                self.wn_en = wn.Wordnet('oewn:2023')
            print("WordNet initialized successfully")
        except ImportError:
            print("Warning: WordNet (wn) library not available")
            self.wn_en = None
    
    def is_available(self) -> bool:
        """Check if WordNet is available."""
        return self.wn_en is not None
    
    def is_animal(self, word: str) -> bool:
        """Check if word represents an animal using WordNet."""
        if not self.is_available():
            return False
        
        try:
            for syn in self.wn_en.synsets(word):
                for h in syn.hypernyms():
                    if any('animal' in lemma for lemma in h.lemmas()):
                        return True
        except Exception:
            pass
        return False
    
    def is_place(self, word: str) -> bool:
        """Check if word represents a place using WordNet."""
        if not self.is_available():
            return False
        
        try:
            for syn in self.wn_en.synsets(word):
                for h in syn.hypernyms():
                    names = h.lemmas()
                    if any(x in names for x in ['city', 'country', 'location']):
                        return True
        except Exception:
            pass
        return False
    
    def is_noun(self, word: str) -> bool:
        """Check if word is a noun using WordNet."""
        if not self.is_available():
            return False
        
        try:
            return any(s.pos == 'n' for s in self.wn_en.synsets(word))
        except Exception:
            return False
    
    def is_adjective(self, word: str) -> bool:
        """Check if word is an adjective using WordNet."""
        if not self.is_available():
            return False
        
        try:
            return any(s.pos == 'a' for s in self.wn_en.synsets(word))
        except Exception:
            return False
    
    def generate_common_nouns(self, words: List[str], max_nouns: int = 10000) -> Set[str]:
        """Generate common nouns from a word list using WordNet."""
        if not self.is_available():
            return set()
        
        common_nouns = set()
        
        for word in words:
            if len(common_nouns) >= max_nouns:
                break
            
            # Only consider single words, not hyphenated or compound
            if not word.isalpha():
                continue
            
            # Exclude capitalized words (likely proper nouns)
            if word[0].isupper():
                continue
            
            # Check if word has a noun synset
            if self.is_noun(word):
                if 2 <= len(word) <= 10:
                    common_nouns.add(word)
        
        return common_nouns


class NullWordNetAnalyzer(WordNetAnalyzer):
    """Null object pattern for when WordNet is not available."""
    
    def is_animal(self, word: str) -> bool:
        return False
    
    def is_place(self, word: str) -> bool:
        return False
    
    def is_noun(self, word: str) -> bool:
        return False
    
    def is_adjective(self, word: str) -> bool:
        return False


def create_wordnet_analyzer() -> WordNetAnalyzer:
    """Factory function to create the appropriate WordNet analyzer."""
    try:
        analyzer = OpenWordNetAnalyzer()
        if analyzer.is_available():
            return analyzer
    except Exception as e:
        print(f"Failed to initialize WordNet analyzer: {e}")
    
    return NullWordNetAnalyzer()
