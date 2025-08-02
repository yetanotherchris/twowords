import pickle
import jellyfish

def remove_similar_names(names):
    unique_names = []
    seen_phonetic = set()
    
    for name in names:
        phonetic_code = jellyfish.metaphone(name)
        
        if phonetic_code not in seen_phonetic:
            unique_names.append(name)
            seen_phonetic.add(phonetic_code)
    
    return unique_names


with open('first_names.pkl', 'rb') as f:
    data = pickle.load(f)

# Pick the first key
first_key = list(data.keys())[0]
print(f"Examining key: '{first_key}'")
print(f"Contents: {data[first_key]}")


uk_names = {}
for name, info in data.items():
    if 'GB' in info['country']:  # GB = Great Britain/UK
        uk_names[name] = info

print(f"Found {len(uk_names)} names that appear in the UK")

# Filter UK names: no spaces and more than 1 character
filtered_uk_names = []
for name in uk_names.keys():
    if (' ' not in name and 
        len(name) > 1 and 
        name.isalpha() and 
        name.isascii() and
        uk_names[name]['country']['GB'] > 0.3):  # At least 10% UK probability
        filtered_uk_names.append(name.lower())

# Remove similar sounding names, e.g. ['alistair', 'alistair', 'alisdair', 'alison']
deduplicated_names = remove_similar_names(filtered_uk_names)

print(f"Found {len(filtered_uk_names)} filtered UK names")
print(f"Found {len(deduplicated_names)} non-similar sounding UK names")
print("First 100:", deduplicated_names[:100])

with open("uk_firstnames.txt", 'w', encoding='utf-8') as f:
    for name in deduplicated_names:
        f.write(name + '\n')