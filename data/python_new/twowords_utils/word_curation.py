import os
import csv
import zipfile
import re
from tqdm import tqdm
from dataclasses import dataclass
from typing import List, Set

WORDS_NEEDED = 110001

@dataclass
class WordScore:
    word: str
    score: float

class WordCurator:
    def __init__(self, words_dir):
        self.words_dir = words_dir

    def is_valid_english_word(self, word: str) -> bool:
        if len(word) > 2 and not any(c in word for c in 'aeiou'):
            return False
        if len(word) <= 4 and word.isupper():
            return False
        consonant_count = 0
        for char in word:
            if char not in 'aeiou':
                consonant_count += 1
                if consonant_count > 3:
                    return False
            else:
                consonant_count = 0
        bad_patterns = ['qq', 'zz', 'xx', 'bv', 'cj', 'cv', 'cw', 'dx', 'fq', 'fx', 'gq', 'gx', 'hx', 'jf', 'jg', 'jq', 'jv', 'jw', 'jx', 'jz', 'kq', 'kx', 'mx', 'px', 'qc', 'qf', 'qg', 'qh', 'qj', 'qk', 'ql', 'qm', 'qn', 'qp', 'qr', 'qs', 'qt', 'qv', 'qw', 'qx', 'qy', 'qz', 'sx', 'vb', 'vf', 'vh', 'vj', 'vm', 'vp', 'vq', 'vt', 'vw', 'vx', 'wq', 'wx', 'xf', 'xj', 'xk', 'xm', 'xp', 'xq', 'xv', 'xw', 'xz', 'zx']
        for pattern in bad_patterns:
            if pattern in word:
                return False
        if len(word) == 1 and word not in ['a', 'i']:
            return False
        if len(word) <= 3 and any(char.isupper() for char in word):
            return False
        if len(word) > 3 and word[-1] not in 'aeiouynslrdtmh':
            return False
        return True

    def is_clearly_english_word(self, word: str) -> bool:
        """Additional strict validation for clearly English words."""
        vowels = sum(1 for c in word if c in 'aeiou')
        if len(word) > 3 and vowels == 0:
            return False
        vowel_ratio = vowels / len(word)
        if vowel_ratio < 0.2 or vowel_ratio > 0.7:
            return False
        if word[0].isupper():
            return False
        if any(pattern * 2 in word for pattern in ['aa', 'ii', 'oo', 'uu']):
            return False
        consonant_clusters = ['bcf', 'bch', 'bdl', 'bdr', 'bgl', 'bkc', 'bkg', 'bkl', 'bkp', 'bkt', 'cpt', 'ctn', 'ctx', 'cwt', 'dbl', 'dft', 'dgr', 'dpt', 'dvt', 'frt', 'gln', 'grd', 'hwy', 'inc', 'ltd', 'mfg', 'mgr', 'pkg', 'pkt', 'plt', 'pnt', 'qty', 'rpt', 'sgt', 'spl', 'std', 'str', 'tbl', 'tmp', 'wgt']
        if any(cluster in word for cluster in consonant_clusters):
            return False
        return True

    def load_words_from_zip(self, zip_path: str) -> List[str]:
        """Load words from curated English word lists, with fallback to zip file."""
        
        # Try to load from Peter Norvig's curated English word list (highest quality)
        norvig_file = os.path.join(self.words_dir, 'norvig-word-list.txt')
        try:
            with open(norvig_file, 'r', encoding='utf-8') as f:
                norvig_words = [line.strip().lower() for line in f if line.strip()]
            
            # Apply basic filtering to Norvig's already-clean list
            filtered_words = []
            for word in norvig_words:
                # Keep words in a reasonable range for memorability
                if len(word) < 2 or len(word) > 10:
                    continue
                
                # Basic validation (Norvig's list should already be clean)
                if not self.is_valid_english_word(word):
                    continue
                    
                filtered_words.append(word)
            
            print(f"Loaded {len(filtered_words):,} quality English words from Norvig's curated list")
            return filtered_words
            
        except FileNotFoundError:
            print(f"Norvig word list not found: {norvig_file}")
            print("Falling back to zip file...")
        
        # Fallback to zip file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Look for the first text file in the zip
                text_files = [f for f in zip_file.namelist() if f.endswith('.txt')]
                if not text_files:
                    raise FileNotFoundError("No text files found in zip")
                
                with zip_file.open(text_files[0]) as f:
                    lines = f.read().decode('utf-8').strip().split('\n')
                    words = [line.strip().lower() for line in lines if line.strip()]
                    
            # Apply strict filtering to zip file words
            filtered_words = []
            for word in words:
                if len(word) < 2 or len(word) > 10:
                    continue
                if not self.is_valid_english_word(word):
                    continue
                if not self.is_clearly_english_word(word):
                    continue
                filtered_words.append(word)
            
            print(f"Fallback: loaded {len(filtered_words):,} filtered words from zip file")
            return filtered_words
            
        except Exception as e:
            print(f"Error loading from zip file: {e}")
            raise FileNotFoundError("No word sources available")

    def load_common_words(self, filepath: str) -> set:
        """Load a large set of common English words from a text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return set(line.strip().lower() for line in f if line.strip() and not line.startswith('#'))
        except FileNotFoundError:
            print(f"Warning: {filepath} not found, skipping large common word bonus.")
            return set()

    def is_common_word(self, word: str) -> bool:
        # Simple check for common English words
        common_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
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
            'both', 'many', 'more', 'than', 'same', 'them', 'what', 'does'}
        return word in common_words

    def is_simple_word(self, word: str) -> bool:
        import re
        if not re.match(r'^[a-z]+$', word):
            return False
        difficult_patterns = [
            'qq', 'xx', 'zz', 'uu', 'ii', 'oo',
            'xh', 'xk', 'xj', 'qw', 'qy',
            'ght', 'pht', 'rht',
        ]
        return not any(pattern in word for pattern in difficult_patterns)

    def load_important_indices(self, file_path: str) -> Set[int]:
        """Load important indices for strategic word placement."""
        indices = set()
        if not os.path.exists(file_path):
            return indices
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    indices.add(int(line))
        return indices

    def load_city_coverage_indices(self, words_dir: str) -> Set[int]:
        """
        Load indices for all UK cities with radius coverage.
        This provides more comprehensive coverage than the basic important_indices.txt.
        """
        # Try to load the enhanced city coverage first
        uk_cities_file = os.path.join(words_dir, 'uk_cities_indices.txt')
        if os.path.exists(uk_cities_file):
            indices = set()
            with open(uk_cities_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse format: CITY_NAME:LAT_INDEX1,LAT_INDEX2|LON_INDEX1,LON_INDEX2
                        if ':' in line:
                            _, indices_part = line.split(':', 1)
                            if '|' in indices_part:
                                lat_part, lon_part = indices_part.split('|', 1)
                                # Add latitude indices
                                for idx_str in lat_part.split(','):
                                    if idx_str.strip():
                                        indices.add(int(idx_str.strip()))
                                # Add longitude indices
                                for idx_str in lon_part.split(','):
                                    if idx_str.strip():
                                        indices.add(int(idx_str.strip()))
            print(f"Loaded {len(indices)} city coverage indices from {uk_cities_file}")
            return indices
        
        # Fallback to regular important_indices.txt
        return self.load_important_indices(os.path.join(words_dir, 'important_indices.txt'))

    def calculate_word_score(self, word: str, food_dishes: Set[str], large_common_words: Set[str] = None) -> WordScore:
        """Calculate a desirability score for a word (higher = better) - enhanced version with WordNet."""
        
        # Import WordNet if available
        try:
            import wn
            # Ensure WordNet is available
            try:
                wn_en = wn.Wordnet('oewn:2023')
            except Exception:
                wn.download('oewn:2023')
                wn_en = wn.Wordnet('oewn:2023')
            
            # Helper functions for WordNet analysis
            def is_animal(w):
                try:
                    for syn in wn_en.synsets(w):
                        for h in syn.hypernyms():
                            if any('animal' in lemma for lemma in h.lemmas()):
                                return True
                except:
                    pass
                return False

            def is_place(w):
                try:
                    for syn in wn_en.synsets(w):
                        for h in syn.hypernyms():
                            names = h.lemmas()
                            if any(x in names for x in ['city', 'country', 'location']):
                                return True
                except:
                    pass
                return False

            def is_noun(w):
                try:
                    return any(s.pos == 'n' for s in wn_en.synsets(w))
                except:
                    return False

            def is_adj(w):
                try:
                    return any(s.pos == 'a' for s in wn_en.synsets(w))
                except:
                    return False
            
            has_wordnet = True
        except ImportError:
            has_wordnet = False
            print("Warning: WordNet not available for enhanced scoring")

        length = len(word)
        is_common = self.is_common_word(word)
        is_simple = self.is_simple_word(word)
        is_food = word in food_dishes
        is_large_common = word in large_common_words if large_common_words else False

        # Base score starts higher for shorter words
        score = 100.0

        # Length penalty (prefer shorter words)
        if length <= 3:
            score += 50  # Very short words get bonus
        elif length <= 4:
            score += 40  # Short words get bonus
        elif length <= 5:
            score += 20  # Short words get bonus
        elif length <= 7:
            score += 0   # Medium words neutral
        elif length <= 10:
            score -= 20  # Long words get penalty
        else:
            score -= 50  # Very long words get big penalty

        # Food dishes get highest priority for populated areas
        if is_food:
            score += 60  # Highest bonus
        
        # Large common words get second highest priority
        if is_large_common:
            score += 55
        
        # Common word bonus (legacy small set)
        if is_common:
            score += 40
        
        # Simple word bonus
        if is_simple:
            score += 20
        
        # Avoid single letters except a few
        if length == 1 and word not in ['a', 'i']:
            score -= 30

        # WordNet-based prioritization
        if has_wordnet:
            if is_animal(word):
                score += 30
            if is_place(word):
                score += 25
            if is_noun(word):
                score += 20
            if is_adj(word):
                score += 15

        # Prefer singular nouns over plurals
        # Penalize likely plurals (ending in 's', 'es', 'ies')
        if length > 3:
            if word.endswith('ies'):
                score -= 15
            elif word.endswith('es'):
                score -= 10
            elif word.endswith('s'):
                score -= 8
            else:
                score += 8  # Likely singular noun

        # Prefer nouns over verbs (simple heuristic)
        # Penalize likely verbs (ending in 'ing', 'ed')
        if word.endswith('ing'):
            score -= 12
        if word.endswith('ed'):
            score -= 8

        # Bonus for matching common noun list (proxy: common_words.txt)
        # If the word is in large_common_words and not a verb/plural, add bonus
        if is_large_common and not word.endswith(('ing', 'ed', 's', 'es', 'ies')):
            score += 10

        return WordScore(word, score)

    def optimize_word_list(self, words: List[str], important_indices: Set[int], food_dishes: List[str], large_common_words: Set[str] = None) -> List[str]:
        """Create an optimized word list with food dishes at important indices."""
        print(f"Optimizing {len(words):,} words for {WORDS_NEEDED:,} positions...")
        print(f"Food dishes available: {len(food_dishes)}")
        
        food_set = set(food_dishes)
        
        # Score all words
        print("Scoring words by desirability...")
        scored_words = [self.calculate_word_score(word, food_set, large_common_words) for word in tqdm(words, desc="Scoring", ncols=80)]
        
        # Sort by score (best first)
        scored_words.sort(key=lambda x: x.score, reverse=True)
        
        # Separate food dishes from other words for strategic placement
        food_words = [sw for sw in scored_words if sw.word in food_set]
        non_food_words = [sw for sw in scored_words if sw.word not in food_set]
        
        print(f"Food dishes found: {len(food_words)}")
        print(f"Best food dishes: {[fw.word for fw in food_words[:20]]}")
        print(f"Important indices count: {len(important_indices)}")
        
        # Create the optimized list - initialize with placeholder words
        optimized = ['placeholder'] * WORDS_NEEDED
        used_words = set()
        
        # FIRST: Place the best FOOD DISHES at ALL important population indices
        important_indices_list = sorted(list(important_indices))
        print(f"Placing FOOD DISHES at {len(important_indices_list)} important indices...")
        
        for i, idx in enumerate(important_indices_list):
            if idx < WORDS_NEEDED and i < len(food_words):
                word = food_words[i].word
                optimized[idx] = word
                used_words.add(word)
                print(f"  Index {idx:6d}: '{word}' (food dish, score: {food_words[i].score:.1f})")
            elif idx < WORDS_NEEDED:
                # Fallback to best non-food word if we run out of food dishes (shouldn't happen)
                if non_food_words:
                    word = non_food_words[0].word
                    optimized[idx] = word
                    used_words.add(word)
                    print(f"  Index {idx:6d}: '{word}' (fallback, score: {non_food_words[0].score:.1f})")
        
        # SECOND: Fill all remaining positions with the best unused words (food + non-food)
        print("Filling remaining positions with best unused words...")
        remaining_words = [sw.word for sw in scored_words if sw.word not in used_words]
        
        fill_index = 0
        for pos in range(WORDS_NEEDED):
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

    def load_wordlist(self, path):
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]

    def generate_common_nouns(self):
        """Generate common nouns dynamically from WordNet and Kaggle data."""
        try:
            import wn
            # Ensure WordNet is available
            try:
                wn_en = wn.Wordnet('oewn:2023')
            except Exception:
                wn.download('oewn:2023')
                wn_en = wn.Wordnet('oewn:2023')

            kaggle_csv_path = os.path.join(self.words_dir, 'kaggle-extracted', 'ngram_freq.csv')
            words = []
            if os.path.exists(kaggle_csv_path):
                with open(kaggle_csv_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for i, row in enumerate(reader):
                        if i >= 50000:
                            break
                        word = row['word'].strip().lower()
                        words.append(word)
            
            common_nouns = set()
            for word in tqdm(words, desc="Finding common nouns"):
                # Only consider single words, not hyphenated or compound
                if not word.isalpha():
                    continue
                # Exclude capitalized words (likely proper nouns)
                if word[0].isupper():
                    continue
                # Check if word has a noun synset
                if any(syn.pos == 'n' for syn in wn_en.synsets(word)):
                    if 2 <= len(word) <= 10:
                        common_nouns.add(word)
            
            # Write to file
            common_nouns_path = os.path.join(self.words_dir, 'common_nouns.txt')
            with open(common_nouns_path, 'w', encoding='utf-8') as f:
                for noun in sorted(common_nouns):
                    f.write(noun + '\n')
            print(f"Generated {len(common_nouns)} common nouns")
            return list(common_nouns)
            
        except ImportError:
            print("Warning: WordNet (wn) not available. Skipping dynamic noun generation.")
            return []

    def curate_words(self):
        """
        Generate a curated list of words prioritizing food dishes, common nouns, and scoring words.
        This follows the logic from words_create_inital_curated_list.py and score_words.py.
        """
        print("Starting word curation...")
        
        # Load food dishes
        food_dishes_path = os.path.join(self.words_dir, 'food_dishes_final.txt')
        food_dishes = self.load_wordlist(food_dishes_path)
        print(f"Loaded {len(food_dishes)} food dishes")

        # Generate common nouns dynamically if possible, otherwise load from file
        common_nouns_path = os.path.join(self.words_dir, 'common_nouns.txt')
        if os.path.exists(common_nouns_path) and os.path.getsize(common_nouns_path) > 0:
            common_nouns = self.load_wordlist(common_nouns_path)
            print(f"Loaded {len(common_nouns)} common nouns from file")
        else:
            common_nouns = self.generate_common_nouns()

        # Load common words
        common_words_path = os.path.join(self.words_dir, 'common_words.txt')
        common_words = self.load_wordlist(common_words_path)
        print(f"Loaded {len(common_words)} common words")

        # Load large common words for enhanced scoring
        large_common_words = self.load_common_words(common_words_path)
        print(f"Loaded {len(large_common_words)} large common words for scoring")

        # Load words from expanded_words files or Norvig list
        expanded_words_path = os.path.join(self.words_dir, 'expanded_words.txt')
        expanded_words_zip_path = os.path.join(self.words_dir, 'expanded_words.zip')
        
        # Prefer optimized_words.txt if it exists, otherwise try other sources
        if os.path.exists(expanded_words_path):
            print(f"Loading words from {expanded_words_path}...")
            with open(expanded_words_path, 'r', encoding='utf-8') as f:
                base_words = [line.strip().lower() for line in f if line.strip()]
        else:
            print(f"Loading words from zip or Norvig list...")
            try:
                base_words = self.load_words_from_zip(expanded_words_zip_path)
            except FileNotFoundError:
                # Use combination approach from original logic
                seen = set()
                base_words = []
                for word in food_dishes + common_nouns + common_words:
                    if word not in seen:
                        seen.add(word)
                        base_words.append(word)

                # Fill remaining words from Kaggle CSV
                kaggle_csv_path = os.path.join(self.words_dir, 'kaggle-extracted', 'ngram_freq.csv')
                kaggle_count = 0
                if os.path.exists(kaggle_csv_path):
                    with open(kaggle_csv_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            word = row['word'].strip().lower()
                            if not word or word in seen:
                                continue
                            seen.add(word)
                            base_words.append(word)
                            kaggle_count += 1
                            if len(base_words) >= WORDS_NEEDED:
                                break
                    print(f"Added {kaggle_count} words from Kaggle CSV")

        words = base_words[:WORDS_NEEDED] if len(base_words) >= WORDS_NEEDED else base_words
        print(f"Using {len(words)} words for optimization")

        # Load important indices and optimize - try enhanced city coverage first
        important_indices_path = os.path.join(self.words_dir, 'important_indices.txt')
        important_indices = self.load_city_coverage_indices(self.words_dir)
        if not important_indices:
            # Fallback to basic important indices
            important_indices = self.load_important_indices(important_indices_path)
        print(f"Loaded {len(important_indices)} important indices for strategic word placement")

        optimized_words = self.optimize_word_list(words, important_indices, food_dishes, large_common_words)
        print(f"Optimized word list with {len(optimized_words)} words")
        
        return optimized_words
