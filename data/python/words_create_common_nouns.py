import os
import wn
from tqdm import tqdm

# Paths

# Set words_dir relative to the new data/words directory
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', '..', 'data')
words_dir = os.path.join(data_dir, 'words')
norvig_file = os.path.join(words_dir, 'norvig-word-list.txt')
output_file = os.path.join(words_dir, 'common_nouns.txt')

# Ensure WordNet is available
try:
    wn_en = wn.Wordnet('oewn:2023')
except Exception:
    wn.download('oewn:2023')
    wn_en = wn.Wordnet('oewn:2023')

# Load Norvig word list
with open(norvig_file, 'r', encoding='utf-8') as f:
    words = [line.strip().lower() for line in f if line.strip()]

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
with open(output_file, 'w', encoding='utf-8') as f:
    for noun in sorted(common_nouns):
        f.write(noun + '\n')

print(f"Wrote {len(common_nouns)} common nouns to {output_file}")
