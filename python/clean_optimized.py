#!/usr/bin/env python3
"""
Enhanced clean.py that places the most popular English words at indices 
corresponding to major UK conurbations and popular areas.

This ensures that coordinates for London, Manchester, Birmingham, etc. 
will map to highly recognizable, common English words.
"""

import random

# Most common English words (frequency-based, suitable for general use)
# These are the most recognizable and frequently used words in English
MOST_POPULAR_WORDS = [
    # Top 100 most common English words
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "as", "you", "do", "at", "this", "but",
    "his", "by", "from", "they", "we", "say", "her", "she", "or", "an",
    "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
    "out", "if", "about", "who", "get", "which", "go", "me", "when", "make",
    "can", "like", "time", "no", "just", "him", "know", "take", "people", "into",
    "year", "your", "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also", "back", "after",
    "use", "two", "how", "our", "work", "first", "well", "way", "even", "new",
    "want", "because", "any", "these", "give", "day", "most", "us", "is", "water",
    
    # Additional highly recognizable words
    "home", "world", "life", "hand", "part", "child", "eye", "woman", "man", "place",
    "work", "week", "case", "point", "government", "company", "number", "group", "problem", "fact",
    "school", "house", "service", "party", "book", "word", "business", "issue", "side", "story",
    "money", "lot", "student", "job", "family", "power", "hour", "game", "line", "end",
    "member", "law", "car", "city", "community", "name", "president", "team", "minute", "idea",
    "kid", "body", "information", "nothing", "ago", "right", "lead", "social", "understand", "whether",
    "back", "watch", "together", "follow", "around", "parent", "only", "stop", "face", "anything",
    "create", "public", "already", "speak", "others", "read", "level", "allow", "add", "office",
    "spend", "door", "health", "person", "art", "sure", "such", "war", "history", "party",
    "within", "grow", "result", "open", "change", "morning", "walk", "reason", "low", "win",
    "research", "girl", "guy", "early", "food", "before", "moment", "himself", "air", "teacher",
    "force", "offer", "enough", "both", "education", "across", "although", "remember", "foot", "second",
    "boy", "maybe", "toward", "able", "age", "off", "policy", "everything", "love", "process",
    "music", "including", "consider", "appear", "actually", "buy", "probably", "human", "serve", "market",
    "die", "send", "expect", "sense", "build", "stay", "fall", "oh", "nation", "plan",
    "cut", "college", "interest", "death", "course", "someone", "experience", "behind", "reach", "local",
    "kill", "six", "remain", "effect", "yeah", "suggest", "class", "control", "raise", "care",
    "perhaps", "little", "late", "hard", "field", "else", "pass", "former", "sell", "major",
    "sometimes", "require", "along", "development", "themselves", "report", "role", "better", "economic", "effort",
    "decide", "rate", "strong", "possible", "heart", "drug", "show", "leader", "light", "voice",
    "wife", "whole", "police", "mind", "finally", "pull", "return", "free", "military", "price",
    
    # Common British English words
    "colour", "favour", "centre", "theatre", "programme", "realise", "organise", "recognise", "travelled", "cancelled",
    "grey", "tyre", "cheque", "defence", "licence", "practise", "analyse", "catalogue", "dialogue", "metre",
    
    # Simple, memorable words perfect for coordinates
    "apple", "bread", "chair", "dance", "earth", "fire", "green", "happy", "island", "jump",
    "kitchen", "lemon", "music", "night", "ocean", "peace", "quiet", "river", "stone", "table",
    "umbrella", "village", "window", "yellow", "zebra", "bridge", "castle", "dragon", "engine", "flower",
    "garden", "hammer", "jungle", "laptop", "monkey", "needle", "orange", "pencil", "rabbit", "spider",
    "tiger", "violin", "wallet", "anchor", "bottle", "candle", "doctor", "elevator", "forest", "guitar",
    "helmet", "igloo", "jacket", "kitten", "ladder", "mirror", "notebook", "oyster", "puzzle", "question",
    "rocket", "sandwich", "tornado", "uniform", "vacuum", "wizard", "xylophone", "yogurt", "zipper"
]

# Load important indices (calculated from major conurbations)
important_lat_indices = set()
important_lon_indices = set()

try:
    with open("important_indices.txt", "r") as f:
        lines = f.readlines()
        reading_lat = True
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                if "longitude" in line.lower():
                    reading_lat = False
                continue
            if line.isdigit():
                if reading_lat:
                    important_lat_indices.add(int(line))
                else:
                    important_lon_indices.add(int(line))
except FileNotFoundError:
    print("Warning: important_indices.txt not found. Using default important indices.")
    # Fallback to calculated indices for major cities
    important_lat_indices = {18224, 24545, 24816, 25073, 27520, 34861, 39547, 43811, 44084, 44808, 48008, 55972, 59782, 68641, 69532}
    important_lon_indices = {20698, 37481, 48117, 48209, 50084, 54121, 57574, 61096, 63822, 64508, 65298, 67423, 68419, 78628, 78722}

print(f"Prioritizing {len(important_lat_indices)} latitude indices and {len(important_lon_indices)} longitude indices")

# Combine all important indices
all_important_indices = important_lat_indices | important_lon_indices
print(f"Total unique important indices: {len(all_important_indices)}")

# Ensure we have enough popular words for all important indices
if len(MOST_POPULAR_WORDS) < len(all_important_indices):
    print(f"Warning: Only {len(MOST_POPULAR_WORDS)} popular words available for {len(all_important_indices)} important indices")

# Load real words from consolidated word list
with open("words_final.txt", "r") as f:
    real_words = set(word.strip().lower() for word in f if word.strip())

# Load proper nouns for pseudo-word generation
with open("proper_nouns.txt", "r") as f:
    proper_nouns = [word.strip().lower() for word in f if word.strip()]

print(f"Loaded {len(real_words)} real words and {len(proper_nouns)} proper nouns")

# Generate compound words by combining existing real words
compound_words = set()
real_words_list = list(real_words)

# Filter words suitable for compounding (3-8 letters, common patterns)
suitable_words = [w for w in real_words_list if 3 <= len(w) <= 8 and w.isalpha()]

print(f"Generating compound words from {len(suitable_words)} suitable base words...")
target_compounds = min(200_000, len(suitable_words) * 2)

while len(compound_words) < target_compounds:
    word1 = random.choice(suitable_words)
    word2 = random.choice(suitable_words)
    compound = word1 + word2
    
    if compound not in real_words and len(compound) <= 15:
        compound_words.add(compound)

print(f"Generated {len(compound_words)} compound words")

# Define prefixes and suffixes for pseudo-word generation
prefixes = [
    "pre", "pro", "de", "re", "un", "ex", "sub", "over",
    "auto", "co", "inter", "mini", "multi", "post", "semi", "super"
]

suffixes = [
    "ing", "ly", "ful", "less", "ment", "able", "ed", "er", 
    "ous", "ive", "ize", "age", "dom", "ship"
]

suitable_proper_nouns = [noun for noun in proper_nouns if 3 <= len(noun) <= 8]
print(f"Using {len(suitable_proper_nouns)} suitable proper nouns for pseudo-word generation")

def generate_pseudo_word():
    """Generate a pseudo-word using English word patterns"""
    pattern = random.choice([1, 2, 3])
    
    if pattern == 1:  # prefix + proper noun
        prefix = random.choice(prefixes)
        noun = random.choice(suitable_proper_nouns)
        word = prefix + noun
        if not (prefix.endswith(noun[0]) and len(noun) > 1):
            return word
        else:
            return prefix + noun[1:]
            
    elif pattern == 2:  # proper noun + suffix  
        noun = random.choice(suitable_proper_nouns)
        suffix = random.choice(suffixes)
        word = noun + suffix
        if not (noun.endswith(suffix[0]) and len(suffix) > 1):
            return word
        else:
            return noun[:-1] + suffix
            
    else:  # prefix + proper noun + suffix
        prefix = random.choice(prefixes)
        noun = random.choice(suitable_proper_nouns)
        suffix = random.choice(suffixes)
        
        if prefix.endswith(noun[0]):
            noun = noun[1:]
        if noun.endswith(suffix[0]):
            noun = noun[:-1]
            
        return prefix + noun + suffix

# Build the complete word list
target_size = 1_040_000
all_words = set(real_words) | compound_words

print(f"Starting with {len(real_words)} real words + {len(compound_words)} compound words = {len(all_words)} total")
print(f"Need {target_size - len(all_words)} more pseudo-words to reach target...")

# Generate remaining pseudo-words to reach target
while len(all_words) < target_size:
    word = generate_pseudo_word()
    if word not in all_words and len(word) >= 4:
        all_words.add(word)

# Convert to sorted list for index-based access
all_words_list = sorted(all_words)

print(f"Created word list with {len(all_words_list)} words")

# Create a new word list with popular words strategically placed
print("Placing popular words at important indices...")

# Start with a copy of the original word list
optimized_words = all_words_list.copy()

# Create a set of words that will be displaced
displaced_words = set()

# Place popular words at important indices
popular_word_index = 0
for important_index in sorted(all_important_indices):
    if important_index < len(optimized_words) and popular_word_index < len(MOST_POPULAR_WORDS):
        # Store the word that's being displaced
        displaced_word = optimized_words[important_index]
        displaced_words.add(displaced_word)
        
        # Place the popular word at this important index
        popular_word = MOST_POPULAR_WORDS[popular_word_index]
        optimized_words[important_index] = popular_word
        
        print(f"Index {important_index:6d}: '{displaced_word}' -> '{popular_word}'")
        popular_word_index += 1

print(f"Placed {popular_word_index} popular words at strategic indices")

# Now place the displaced words back into available positions
# Find positions that don't contain popular words
available_positions = []
popular_words_set = set(MOST_POPULAR_WORDS[:popular_word_index])

for i, word in enumerate(optimized_words):
    if word not in popular_words_set and i not in all_important_indices:
        available_positions.append(i)

print(f"Found {len(available_positions)} available positions for displaced words")

# Place displaced words in available positions
displaced_words_list = list(displaced_words)
random.shuffle(displaced_words_list)

for i, displaced_word in enumerate(displaced_words_list):
    if i < len(available_positions):
        pos = available_positions[i]
        optimized_words[pos] = displaced_word

# Write the optimized word list
with open("expanded_words.txt", "w") as f:
    for word in optimized_words:
        f.write(f"{word}\n")

print(f"\nOptimized word list created: {len(optimized_words)} words in 'expanded_words.txt'")
print(f"Real words: {len(real_words):,}")
print(f"Compound words: {len(compound_words):,}")
print(f"Pseudo-words: {len(all_words) - len(real_words) - len(compound_words):,}")
print(f"Popular words strategically placed: {popular_word_index}")

# Verify some important indices
print(f"\nSample mappings for major cities:")
sample_indices = [25073, 44808, 34861, 48008, 68641]  # London, Manchester, Birmingham, Leeds, Glasgow
for idx in sample_indices:
    if idx < len(optimized_words):
        print(f"Index {idx:6d}: '{optimized_words[idx]}'")
