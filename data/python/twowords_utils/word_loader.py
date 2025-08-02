"""
Word loading utilities for the TwoWords project.
Handles loading words from various sources including files, zip archives, and CSV data.

Attribution: 
- Kaggle ngram frequency data
- Peter Norvig's word list
- WordNet data
"""

import os
import csv
import zipfile
from typing import List, Set
from abc import ABC, abstractmethod


class WordLoader(ABC):
    """Abstract base class for word loading."""
    
    @abstractmethod
    def load_words(self) -> List[str]:
        """Load words from the source."""
        pass


class FileWordLoader(WordLoader):
    """Loads words from a text file."""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        self.file_path = file_path
        self.encoding = encoding
    
    def load_words(self) -> List[str]:
        """Load words from text file."""
        if not os.path.exists(self.file_path):
            print(f"Warning: {self.file_path} not found.")
            return []
        
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            return [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]


class KaggleCSVWordLoader(WordLoader):
    """Loads words from Kaggle CSV data in a zip file."""
    
    def __init__(self, zip_path: str, max_words: int = None):
        self.zip_path = zip_path
        self.max_words = max_words
    
    def load_words(self) -> List[str]:
        """Load words from Kaggle CSV in zip file."""
        if not os.path.exists(self.zip_path):
            raise FileNotFoundError(f"Kaggle zip file not found: {self.zip_path}")
        
        words = []
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_file:
                with zip_file.open('ngram_freq.csv') as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                    reader = csv.DictReader(csv_content.splitlines())
                    
                    for row in reader:
                        word = row['word'].strip().lower()
                        if word and word.isalpha():
                            words.append(word)
                            
                        # Stop when we have enough words
                        if self.max_words and len(words) >= self.max_words:
                            break
            
            print(f"Loaded {len(words):,} words from Kaggle CSV")
            return words
            
        except Exception as e:
            print(f"Error loading from Kaggle zip: {e}")
            raise


class ZipFileWordLoader(WordLoader):
    """Loads words from text files in a zip archive."""
    
    def __init__(self, zip_path: str):
        self.zip_path = zip_path
    
    def load_words(self) -> List[str]:
        """Load words from text files in zip archive."""
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_file:
                # Look for text files in the zip
                text_files = [f for f in zip_file.namelist() if f.endswith('.txt')]
                if not text_files:
                    raise FileNotFoundError("No text files found in zip")
                
                with zip_file.open(text_files[0]) as f:
                    lines = f.read().decode('utf-8').strip().split('\n')
                    words = [line.strip().lower() for line in lines if line.strip()]
            
            print(f"Loaded {len(words):,} words from zip file")
            return words
            
        except Exception as e:
            print(f"Error loading from zip file: {e}")
            raise


class CompositeWordLoader(WordLoader):
    """Combines multiple word loaders and deduplicates results."""
    
    def __init__(self, loaders: List[WordLoader]):
        self.loaders = loaders
    
    def load_words(self) -> List[str]:
        """Load words from all loaders and deduplicate."""
        all_words = []
        seen = set()
        
        for loader in self.loaders:
            try:
                words = loader.load_words()
                for word in words:
                    if word not in seen:
                        seen.add(word)
                        all_words.append(word)
            except Exception as e:
                print(f"Error loading from {type(loader).__name__}: {e}")
                continue
        
        return all_words


class IndicesLoader:
    """Loads important indices from a file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load_indices(self) -> Set[int]:
        """Load important indices from file."""
        indices = set()
        if not os.path.exists(self.file_path):
            return indices
        
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        indices.add(int(line))
                    except ValueError:
                        print(f"Warning: Invalid index value: {line}")
        
        return indices


class WordListFactory:
    """Factory for creating word loaders based on configuration."""
    
    def __init__(self, words_dir: str):
        self.words_dir = words_dir
    
    def create_kaggle_loader(self, max_words: int = None) -> KaggleCSVWordLoader:
        """Create a Kaggle CSV word loader."""
        kaggle_zip_path = os.path.join(self.words_dir, 'kaggle.zip')
        return KaggleCSVWordLoader(kaggle_zip_path, max_words)
    
    def create_file_loader(self, filename: str) -> FileWordLoader:
        """Create a file word loader."""
        file_path = os.path.join(self.words_dir, filename)
        return FileWordLoader(file_path)
    
    def create_comprehensive_loader(self, max_kaggle_words: int = None) -> CompositeWordLoader:
        """Create a loader that combines all available sources."""
        loaders = []
        
        # Try to load from specific files first
        file_sources = [
            'food_dishes_final.txt',
            'common_nouns.txt', 
            'common_words.txt',
            'expanded_words.txt'
        ]
        
        for filename in file_sources:
            file_path = os.path.join(self.words_dir, filename)
            if os.path.exists(file_path):
                loaders.append(self.create_file_loader(filename))
        
        # Add Kaggle loader if available
        kaggle_zip_path = os.path.join(self.words_dir, 'kaggle.zip')
        if os.path.exists(kaggle_zip_path):
            loaders.append(self.create_kaggle_loader(max_kaggle_words))
        
        # Add regular zip loader as fallback
        words_zip_path = os.path.join(self.words_dir, 'words.zip')
        if os.path.exists(words_zip_path):
            loaders.append(ZipFileWordLoader(words_zip_path))
        
        return CompositeWordLoader(loaders)
    
    def create_indices_loader(self, filename: str = 'important_indices.txt') -> IndicesLoader:
        """Create an indices loader."""
        file_path = os.path.join(self.words_dir, filename)
        return IndicesLoader(file_path)
