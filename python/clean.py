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

# Step 3: Define more pronounceable English syllables for pseudo-words
# Based on common English phonetic patterns and prefixes/suffixes
syllables = [
    # Common prefixes
    "pre", "pro", "de", "re", "un", "in", "ex", "con", "sub", "over",
    # Vowel-consonant patterns
    "al", "ar", "er", "or", "en", "an", "on", "el", "il", "ul",
    # Consonant-vowel patterns  
    "ba", "be", "bi", "bo", "bu", "ca", "ce", "ci", "co", "cu",
    "da", "de", "di", "do", "du", "fa", "fe", "fi", "fo", "fu",
    "ga", "ge", "gi", "go", "gu", "ha", "he", "hi", "ho", "hu",
    "ja", "je", "ji", "jo", "ju", "ka", "ke", "ki", "ko", "ku",
    "la", "le", "li", "lo", "lu", "ma", "me", "mi", "mo", "mu",
    "na", "ne", "ni", "no", "nu", "pa", "pe", "pi", "po", "pu",
    "ra", "re", "ri", "ro", "ru", "sa", "se", "si", "so", "su",
    "ta", "te", "ti", "to", "tu", "va", "ve", "vi", "vo", "vu",
    "wa", "we", "wi", "wo", "wu", "ya", "ye", "yi", "yo", "yu",
    "za", "ze", "zi", "zo", "zu",
    # Common English endings
    "ing", "tion", "ly", "ful", "less", "ness", "ment", "able", "ible",
    # Double consonants with vowels
    "ble", "ple", "tle", "dle", "gle", "cle", "fle"
]

# Step 4: Combine all word types and generate remaining pseudo-words if needed
target_size = 1_040_000
all_words = set(real_words) | compound_words

def generate_pseudo_word():
    """Generate a pseudo-word by combining 2-3 pronounceable syllables"""
    num_syllables = random.choice([2, 3])  # Shorter words are more natural
    return ''.join(random.choices(syllables, k=num_syllables))

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
