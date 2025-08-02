import wn
from tqdm import tqdm

# Download WordNet data if needed
try:
    list(wn.synsets(pos='n', limit=1))
except:
    print("Downloading WordNet data...")
    wn.download('ewn:2020')
    print("Download complete!")

def get_words_by_pos(pos, pos_name):
    """Get all words of a specific part of speech with progress bar"""
    print(f"Getting all {pos_name} synsets...")
    synsets = list(wn.synsets(pos=pos))
    
    words = set()
    
    print(f"Extracting {pos_name} from {len(synsets)} synsets...")
    for synset in tqdm(synsets, desc=f"Processing {pos_name} synsets"):
        for word in synset.words():
            word_text = word.lemma()
            # Filter for words between 3-8 characters (inclusive)
            if (3 <= len(word_text) <= 8 and word_text.isalpha()):
                words.add(word_text.lower())
    
    return sorted(list(words))

def get_all_nouns():
    """Get all nouns from WordNet with progress bar"""
    return get_words_by_pos('n', 'noun')

def get_all_adjectives():
    """Get all adjectives from WordNet with progress bar"""
    return get_words_by_pos('a', 'adjective')

def get_all_verbs():
    """Get all verbs from WordNet with progress bar"""
    return get_words_by_pos('v', 'verb')

if __name__ == "__main__":
    # Get nouns
    print("=" * 50)
    print("EXTRACTING NOUNS")
    print("=" * 50)
    nouns = get_all_nouns()
    print(f"\nFound {len(nouns)} unique nouns (4-6 characters)")
    
    # Show first 10 filtered nouns as example
    print("\nFirst 10 filtered nouns:")
    for i, noun in enumerate(nouns[:10], 1):
        print(f"{i:2d}. {noun} ({len(noun)} chars)")
    
    # Save nouns to file
    print(f"\nSaving all {len(nouns)} filtered nouns to 'wordnet_nouns_filtered.txt'...")
    with open('wordnet_nouns_filtered.txt', 'w', encoding='utf-8') as f:
        for noun in nouns:
            f.write(noun + '\n')
    print("Nouns saved!")
    
    # Get adjectives
    print("\n" + "=" * 50)
    print("EXTRACTING ADJECTIVES")
    print("=" * 50)
    adjectives = get_all_adjectives()
    print(f"\nFound {len(adjectives)} unique adjectives (4-6 characters)")
    
    # Show first 10 filtered adjectives as example
    print("\nFirst 10 filtered adjectives:")
    for i, adj in enumerate(adjectives[:10], 1):
        print(f"{i:2d}. {adj} ({len(adj)} chars)")
    
    # Save adjectives to file
    print(f"\nSaving all {len(adjectives)} filtered adjectives to 'wordnet_adjectives_filtered.txt'...")
    with open('wordnet_adjectives_filtered.txt', 'w', encoding='utf-8') as f:
        for adj in adjectives:
            f.write(adj + '\n')
    print("Adjectives saved!")
    
    # Get verbs
    print("\n" + "=" * 50)
    print("EXTRACTING VERBS")
    print("=" * 50)
    verbs = get_all_verbs()
    print(f"\nFound {len(verbs)} unique verbs (4-6 characters)")
    
    # Show first 10 filtered verbs as example
    print("\nFirst 10 filtered verbs:")
    for i, verb in enumerate(verbs[:10], 1):
        print(f"{i:2d}. {verb} ({len(verb)} chars)")
    
    # Save verbs to file
    print(f"\nSaving all {len(verbs)} filtered verbs to 'wordnet_verbs_filtered.txt'...")
    with open('wordnet_verbs_filtered.txt', 'w', encoding='utf-8') as f:
        for verb in verbs:
            f.write(verb + '\n')
    print("Verbs saved!")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Nouns: {len(nouns)} words")
    print(f"Adjectives: {len(adjectives)} words")
    print(f"Verbs: {len(verbs)} words")
    print(f"Total: {len(nouns) + len(adjectives) + len(verbs)} words")
    print("\nAll files saved successfully!")