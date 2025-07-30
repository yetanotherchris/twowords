import random

# Step 1: Load real words from words_alpha.txt
with open("words_alpha.txt", "r") as f:
    real_words = set(word.strip().lower() for word in f if word.strip())

# Step 2: Define syllables to generate pseudo-words
syllables = [
    "ba", "be", "bi", "bo", "bu",
    "da", "de", "di", "do", "du",
    "ka", "ke", "ki", "ko", "ku",
    "la", "le", "li", "lo", "lu",
    "ma", "me", "mi", "mo", "mu",
    "na", "ne", "ni", "no", "nu",
    "ra", "re", "ri", "ro", "ru",
    "sa", "se", "si", "so", "su",
    "ta", "te", "ti", "to", "tu",
    "za", "ze", "zi", "zo", "zu"
]

# Step 3: Generate unique pseudo-words until we reach the total
target_size = 1_040_000
all_words = set(real_words)

def generate_pseudo_word():
    return ''.join(random.choices(syllables, k=random.choice([3, 4])))

while len(all_words) < target_size:
    word = generate_pseudo_word()
    if word not in all_words:
        all_words.add(word)

# Step 4: Write the combined set to a new file
with open("expanded_words.txt", "w") as f:
    for word in sorted(all_words):
        f.write(f"{word}\n")

print(f"Generated {len(all_words)} words in 'expanded_words.txt'")
