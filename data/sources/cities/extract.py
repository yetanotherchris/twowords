import csv

def filter_names_from_csv(file_path):
    valid_names = []
    valid_subcountries = {"england", "wales", "scotland"}
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['subcountry'].lower() in valid_subcountries:
                name = row['name']
                if ' ' not in name and name.isalpha() and name.isascii():
                    valid_names.append(name.lower())
    
    return valid_names

# Example usage
file_path = 'world-cities.csv'
result = filter_names_from_csv(file_path)
result.sort()

with open("uk_cities.txt", 'w', encoding='utf-8') as f:
    for word in result:
        f.write(word + '\n')

print(f"Found {len(result)} names that appear in the UK")
