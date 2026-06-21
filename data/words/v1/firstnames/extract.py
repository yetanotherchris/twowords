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


all_names = {}
for name, info in data.items():
    if 'GB' in info['country']: # or 'US' in info['country']: 
        all_names[name] = info

print(f"Found {len(all_names)} names that appear in the U/US")

# Filter names
filtered_all_names = []
for name in all_names.keys():
    if (' ' not in name and 
        len(name) > 1 and name.isalpha() and name.isascii()):
        country = all_names[name].get('country', {})  # Safely get 'country' as empty dict if missing
        us_prob = country.get('US', 0)  # Default to 0 if 'US' missing
        gb_prob = country.get('GB', 0)  # Default to 0 if 'GB' missing
        if gb_prob > 0.1:  # At least 20% US or 30% GB probability
            filtered_all_names.append(name.lower())

# Remove similar sounding names, e.g. ['alistair', 'alistair', 'alisdair', 'alison']
#filtered_all_names = remove_similar_names(filtered_all_names)

print(f"Found {len(filtered_all_names)} filtered UK names")
print(f"Found {len(filtered_all_names)} non-similar sounding UK names")
print("First 100:", filtered_all_names[:100])

with open("uk_firstnames.txt", 'w', encoding='utf-8') as f:
    for name in filtered_all_names:
        f.write(name + '\n')