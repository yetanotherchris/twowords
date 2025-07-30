#!/usr/bin/env python3

with open('expanded_words.txt', 'r') as f:
    words = [line.strip() for line in f]

# Test specific indices for major cities
test_indices = {
    25073: 'London (lat)',
    78722: 'London (lon)', 
    44808: 'Manchester (lat)',
    57574: 'Manchester (lon)',
    34861: 'Birmingham (lat)',
    61096: 'Birmingham (lon)',
    68641: 'Glasgow (lat)',
    37481: 'Glasgow (lon)'
}

print('Verification of popular words at major city indices:')
print('=' * 55)
for idx, location in test_indices.items():
    if idx < len(words):
        print(f'{location:20} | Index {idx:6d}: "{words[idx]}"')
    else:
        print(f'{location:20} | Index {idx:6d}: OUT OF RANGE')
