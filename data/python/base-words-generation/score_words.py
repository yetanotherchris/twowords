#!/usr/bin/env python3
"""
TwoWords API - Word List Optimizer

Builds an optimized word list for the TwoWords API.
Prioritizes food dishes, common nouns, and common words, then fills from Norvig's list.
Words are scored for memorability and placed at key indices for UK population centers.
"""

import os
import zipfile
from tqdm import tqdm
from dataclasses import dataclass
from typing import List, Set

WORDS_NEEDED = 110001

@dataclass
class WordScore:
    word: str
    score: float

def is_valid_english_word(word: str) -> bool:
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

def is_clearly_english_word(word: str) -> bool:
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

def is_common_word(word: str) -> bool:
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

def is_simple_word(word: str) -> bool:
    import re
    if not re.match(r'^[a-z]+$', word):
        return False
    difficult_patterns = [
        'qq', 'xx', 'zz', 'uu', 'ii', 'oo',
        'xh', 'xk', 'xj', 'qw', 'qy',
        'ght', 'pht', 'rht',
    ]
    return not any(pattern in word for pattern in difficult_patterns)

def load_important_indices(file_path: str) -> Set[int]:
    indices = set()
    if not os.path.exists(file_path):
        return indices
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                indices.add(int(line))
    return indices

def calculate_word_score(word: str, food_dishes: Set[str]) -> WordScore:
    length = len(word)
    score = 100.0
    if length <= 3:
        score += 50
    elif length <= 4:
        score += 40
    elif length <= 5:
        score += 20
    elif length <= 7:
        score += 0
    elif length <= 10:
        score -= 20
    else:
        score -= 50
    if word in food_dishes:
        score += 60
    if is_common_word(word):
        score += 40
    if is_simple_word(word):
        score += 20
    if length == 1 and word not in ['a', 'i']:
        score -= 30
    if length > 3:
        if word.endswith('ies'):
            score -= 15
        elif word.endswith('es'):
            score -= 10
        elif word.endswith('s'):
            score -= 8
        else:
            score += 8
    if word.endswith('ing'):
        score -= 12
    if word.endswith('ed'):
        score -= 8
    return WordScore(word, score)

def optimize_word_list(words: List[str], important_indices: Set[int], food_dishes: List[str]) -> List[str]:
    food_set = set(food_dishes)
    scored_words = [calculate_word_score(word, food_set) for word in tqdm(words, desc="Scoring", ncols=80)]
    scored_words.sort(key=lambda x: x.score, reverse=True)
    food_words = [sw for sw in scored_words if sw.word in food_set]
    non_food_words = [sw for sw in scored_words if sw.word not in food_set]
    optimized = ['placeholder'] * WORDS_NEEDED
    used_words = set()
    important_indices_list = sorted(list(important_indices))
    for i, idx in enumerate(important_indices_list):
        if idx < WORDS_NEEDED and i < len(food_words):
            word = food_words[i].word
            optimized[idx] = word
            used_words.add(word)
        elif idx < WORDS_NEEDED:
            word = non_food_words[0].word
            optimized[idx] = word
            used_words.add(word)
    remaining_words = [sw.word for sw in scored_words if sw.word not in used_words]
    fill_index = 0
    for pos in range(WORDS_NEEDED):
        if optimized[pos] == 'placeholder':
            if fill_index < len(remaining_words):
                optimized[pos] = remaining_words[fill_index]
                fill_index += 1
            else:
                optimized[pos] = f"word{pos}"
    return optimized

def save_optimized_words(words: List[str], output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(f"{word}\n")

def main():
    print("TwoWords API - Word List Optimizer\n" + "=" * 40)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(parent_dir, '..', 'data')
    words_dir = os.path.join(data_dir, 'words')
    output_dir = os.path.join(data_dir, 'output')
    food_dishes_path = os.path.join(words_dir, 'food_dishes_final.txt')
    common_nouns_path = os.path.join(words_dir, 'common_nouns.txt')
    common_words_path = os.path.join(words_dir, 'common_words.txt')
    kaggle_csv_path = os.path.join(words_dir, 'kaggle-extracted', 'ngram_freq.csv')
    output_file = os.path.join(output_dir, 'words.txt')
    important_indices_path = os.path.join(words_dir, 'important_indices.txt')

    def load_wordlist(path):
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]

    food_dishes = load_wordlist(food_dishes_path)
    common_nouns = load_wordlist(common_nouns_path)
    common_words = load_wordlist(common_words_path)
    seen = set()
    base_words = []
    for word in food_dishes + common_nouns + common_words:
        if word not in seen:
            seen.add(word)
            base_words.append(word)

    # Fill remaining words from Kaggle CSV (most popular words)
    import csv
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
        print(f"Loaded {kaggle_count} additional words from Kaggle CSV.")
    else:
        print(f"Warning: Kaggle CSV not found at {kaggle_csv_path}. No additional words loaded.")

    words = base_words[:WORDS_NEEDED]
    print(f"Loaded {len(words)} words for optimization.")

    important_indices = load_important_indices(important_indices_path)
    optimized_words = optimize_word_list(words, important_indices, food_dishes)
    os.makedirs(output_dir, exist_ok=True)
    save_optimized_words(optimized_words, output_file)
    print(f"Saved optimized word list to {output_file}")

if __name__ == "__main__":
    main()
