"""
Word list optimization utilities for the TwoWords project.
Handles strategic placement of words in optimized lists.

Attribution: Optimization algorithms based on TwoWords project requirements
"""

import random
from typing import List, Set
from tqdm import tqdm
from .word_scorer import WordScorer, WordScore


class WordListOptimizer:
    """Optimizes word placement in lists for strategic positioning."""
    
    def __init__(self, word_scorer: WordScorer = None):
        self.word_scorer = word_scorer or WordScorer()
    
    def optimize_word_list(self, words: List[str], important_indices: Set[int], 
                          food_dishes: List[str], large_common_words: Set[str] = None,
                          words_needed: int = 110001) -> List[str]:
        """Create an optimized word list with food dishes at important indices."""
        print(f"Optimizing {len(words):,} words for {words_needed:,} positions...")
        print(f"Food dishes available: {len(food_dishes)}")
        
        food_set = set(food_dishes)
        
        # Score all words
        print("Scoring words by desirability...")
        scored_words = []
        for word in tqdm(words, desc="Scoring", ncols=80):
            score = self.word_scorer.calculate_score(word, food_set, large_common_words)
            scored_words.append(score)
        
        # Sort by score (best first)
        scored_words.sort(key=lambda x: x.score, reverse=True)
        
        # Separate food dishes from other words for strategic placement
        food_words = [sw for sw in scored_words if sw.word in food_set]
        non_food_words = [sw for sw in scored_words if sw.word not in food_set]
        
        print(f"Food dishes found: {len(food_words)}")
        print(f"Best food dishes: {[fw.word for fw in food_words[:20]]}")
        print(f"Important indices count: {len(important_indices)}")
        
        # Create the optimized list - initialize with placeholder words
        optimized = ['placeholder'] * words_needed
        used_words = set()
        
        # FIRST: Place the best FOOD DISHES at ALL important population indices
        important_indices_list = sorted(list(important_indices))
        print(f"Placing FOOD DISHES at {len(important_indices_list)} important indices...")
        
        fallback_index = 0  # Track which non-food word to use next for fallbacks
        for i, idx in enumerate(important_indices_list):
            if idx < words_needed and i < len(food_words):
                word = food_words[i].word
                optimized[idx] = word
                used_words.add(word)
                print(f"  Index {idx:6d}: '{word}' (food dish, score: {food_words[i].score:.1f})")
            elif idx < words_needed:
                # Fallback to best non-food word if we run out of food dishes
                if fallback_index < len(non_food_words):
                    word = non_food_words[fallback_index].word
                    optimized[idx] = word
                    used_words.add(word)
                    print(f"  Index {idx:6d}: '{word}' (fallback, score: {non_food_words[fallback_index].score:.1f})")
                    fallback_index += 1  # Move to next non-food word
        
        # SECOND: Fill all remaining positions with the best unused words (food + non-food)
        print("Filling remaining positions with best unused words...")
        remaining_words = [sw.word for sw in scored_words if sw.word not in used_words]
        
        fill_index = 0
        for pos in range(words_needed):
            if optimized[pos] == 'placeholder':  # Position not filled yet
                if fill_index < len(remaining_words):
                    optimized[pos] = remaining_words[fill_index]
                    fill_index += 1
                else:
                    # Fallback if we run out (shouldn't happen)
                    optimized[pos] = f"word{pos}"
        
        # Verify no placeholder positions remain
        placeholders = [i for i, word in enumerate(optimized) if word == 'placeholder']
        if placeholders:
            print(f"Warning: {len(placeholders)} placeholder positions remain!")
        
        return optimized
    
    def create_cities_only_list(self, quality_words: List[str], important_indices: Set[int]) -> List[str]:
        """Generate a smaller word list that only covers major UK cities."""
        print("Starting cities-only word generation...")
        
        if not important_indices:
            print("Warning: No important indices found. Creating minimal word list.")
            return ["placeholder"] * 1000  # Minimal fallback
        
        # Filter for 4-7 character words
        filtered_words = [
            word for word in quality_words 
            if 4 <= len(word) <= 7 and word.isalpha()
        ]
        
        print(f"Collected {len(filtered_words)} quality 4-7 character words")
        
        # Calculate how many words we need
        max_index = max(important_indices) if important_indices else 0
        words_needed = max_index + 1
        print(f"Need {words_needed:,} words to cover highest city index ({max_index:,})")
        
        # Create word list with placeholders
        cities_words = ["UNUSED"] * words_needed
        
        # Shuffle words for distribution across cities
        random.seed(42)  # Reproducible shuffling
        random.shuffle(filtered_words)
        
        # Place words at ALL important indices (full city coverage)
        word_index = 0
        indices_filled = 0
        for city_index in sorted(important_indices):
            if word_index < len(filtered_words):
                cities_words[city_index] = filtered_words[word_index]
                word_index += 1
                indices_filled += 1
                # Only print first few and last few to avoid spam
                if indices_filled <= 5 or indices_filled > len(important_indices) - 5:
                    print(f"  City index {city_index:6d}: '{filtered_words[word_index-1]}'")
                elif indices_filled == 6:
                    print("  ... (continuing to fill all city indices)")
            else:
                # If we run out of quality words, cycle through them again
                cities_words[city_index] = filtered_words[word_index % len(filtered_words)]
                word_index += 1
                indices_filled += 1
        
        print(f"Cities-only word list created with {len(cities_words):,} total positions")
        print(f"Actual words placed at {indices_filled} city locations")
        print(f"Unused positions: {cities_words.count('UNUSED'):,}")
        
        return cities_words


class WordPlacementStrategy:
    """Strategy pattern for different word placement approaches."""
    
    def place_words(self, words: List[str], indices: Set[int], total_positions: int) -> List[str]:
        """Place words according to the strategy."""
        raise NotImplementedError


class OptimalPlacementStrategy(WordPlacementStrategy):
    """Places highest-scoring words at most important positions."""
    
    def __init__(self, word_scorer: WordScorer):
        self.word_scorer = word_scorer
    
    def place_words(self, words: List[str], indices: Set[int], total_positions: int) -> List[str]:
        """Place words optimally based on scores."""
        # Score and sort words
        scored_words = self.word_scorer.score_words(words)
        
        result = ["unused"] * total_positions
        word_index = 0
        
        # Fill important indices first
        for idx in sorted(indices):
            if idx < total_positions and word_index < len(scored_words):
                result[idx] = scored_words[word_index].word
                word_index += 1
        
        # Fill remaining positions
        for pos in range(total_positions):
            if result[pos] == "unused" and word_index < len(scored_words):
                result[pos] = scored_words[word_index].word
                word_index += 1
        
        return result


class RandomPlacementStrategy(WordPlacementStrategy):
    """Places words randomly for testing/comparison."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def place_words(self, words: List[str], indices: Set[int], total_positions: int) -> List[str]:
        """Place words randomly."""
        random.seed(self.seed)
        shuffled_words = words.copy()
        random.shuffle(shuffled_words)
        
        result = ["unused"] * total_positions
        word_index = 0
        
        # Fill important indices first
        for idx in sorted(indices):
            if idx < total_positions and word_index < len(shuffled_words):
                result[idx] = shuffled_words[word_index]
                word_index += 1
        
        # Fill remaining positions
        for pos in range(total_positions):
            if result[pos] == "unused" and word_index < len(shuffled_words):
                result[pos] = shuffled_words[word_index]
                word_index += 1
        
        return result
