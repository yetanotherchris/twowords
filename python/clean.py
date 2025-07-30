import random

# Word List Source Information:
# ============================
# Original source: dwyl/english-words GitHub repository
# URL: https://github.com/dwyl/english-words
# 
# Final consolidated file: words_final.txt (416,296 words)
# - Downloaded from: https://raw.githubusercontent.com/dwyl/english-words/master/words.txt
# - Filtered with PowerShell: Get-Content words_comprehensive.txt | Where-Object { $_ -match "^[a-zA-Z]+$" }
# - Removed 50,254 words containing numbers, punctuation, or special characters
# - Preserves modern terms (USB, email, internet, covid) and proper names (Deborah)

# Step 1: Load real words from consolidated word list
with open("words_final.txt", "r") as f:
    real_words = set(word.strip().lower() for word in f if word.strip())

# Load proper nouns for pseudo-word generation
with open("proper_nouns.txt", "r") as f:
    proper_nouns = [word.strip().lower() for word in f if word.strip()]

print(f"Loaded {len(real_words)} real words and {len(proper_nouns)} proper nouns")

# Step 2: Generate compound words by combining existing real words
# Examples: "redhouse", "cheesehorse", "bluewater", "quickfire"
compound_words = set()
real_words_list = list(real_words)

# Filter words suitable for compounding (3-8 letters, common patterns)
suitable_words = [w for w in real_words_list if 3 <= len(w) <= 8 and w.isalpha()]

print(f"Generating compound words from {len(suitable_words)} suitable base words...")
target_compounds = min(200_000, len(suitable_words) * 2)  # Generate up to 200k compounds

while len(compound_words) < target_compounds:
    # Pick two random words and combine them
    word1 = random.choice(suitable_words)
    word2 = random.choice(suitable_words)
    compound = word1 + word2
    
    # Only add if it's not already a real word and not too long
    if compound not in real_words and len(compound) <= 15:
        compound_words.add(compound)

print(f"Generated {len(compound_words)} compound words")

# Step 3: Define English prefixes and suffixes that work well with proper nouns
# Filtered to avoid awkward combinations and focus on natural-sounding word formation
prefixes = [
    "pre", "pro", "de", "re", "un", "ex", "sub", "over",
    "auto", "co", "inter", "mini", "multi", "post", "semi", "super"
]

suffixes = [
    "ing", "ly", "ful", "less", "ment", "able", "ed", "er", 
    "ous", "ive", "ize", "age", "dom", "ship"
]

# Filter proper nouns for better word formation (shorter, more suitable)
suitable_proper_nouns = [noun for noun in proper_nouns if 3 <= len(noun) <= 8]
print(f"Using {len(suitable_proper_nouns)} suitable proper nouns (3-8 letters) for pseudo-word generation")

# Step 4: Combine all word types and generate remaining pseudo-words if needed
target_size = 1_040_000
all_words = set(real_words) | compound_words

def generate_pseudo_word():
    """Generate a pseudo-word using English word patterns: prefix + proper noun + suffix"""
    # Generate different patterns
    pattern = random.choice([1, 2, 3])
    
    if pattern == 1:  # prefix + proper noun
        prefix = random.choice(prefixes)
        noun = random.choice(suitable_proper_nouns)
        word = prefix + noun
        # Avoid awkward double letters at junction
        if not (prefix.endswith(noun[0]) and len(noun) > 1):
            return word
        else:
            return prefix + noun[1:]  # Skip first letter to avoid double
            
    elif pattern == 2:  # proper noun + suffix  
        noun = random.choice(suitable_proper_nouns)
        suffix = random.choice(suffixes)
        word = noun + suffix
        # Avoid awkward double letters at junction
        if not (noun.endswith(suffix[0]) and len(suffix) > 1):
            return word
        else:
            return noun[:-1] + suffix  # Remove last letter to avoid double
            
    else:  # prefix + proper noun + suffix
        prefix = random.choice(prefixes)
        noun = random.choice(suitable_proper_nouns)
        suffix = random.choice(suffixes)
        
        # Handle potential double letters
        if prefix.endswith(noun[0]):
            noun = noun[1:]
        if noun.endswith(suffix[0]):
            noun = noun[:-1]
            
        return prefix + noun + suffix

print(f"Starting with {len(real_words)} real words + {len(compound_words)} compound words = {len(all_words)} total")
print(f"Need {target_size - len(all_words)} more pseudo-words to reach target...")

# Generate remaining pseudo-words to reach target
while len(all_words) < target_size:
    word = generate_pseudo_word()
    if word not in all_words and len(word) >= 4:  # Minimum 4 characters
        all_words.add(word)

# Step 5: Write the combined set to a new file
# Output contains: real English words + compound words + generated pseudo-words, all alphabetically sorted
with open("expanded_words.txt", "w") as f:
    for word in sorted(all_words):
        f.write(f"{word}\n")

print(f"\nFinal word list created: {len(all_words)} words in 'expanded_words.txt'")
print(f"Real words: {len(real_words):,}")
print(f"Compound words: {len(compound_words):,}")
print(f"Pseudo-words: {len(all_words) - len(real_words) - len(compound_words):,}")
