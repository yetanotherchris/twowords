1. script to clean up kaggle.zip/ngram_freq.csv:
 1. convert the csv to text file, take the first column
 2. Starting from the first line, take all min 3 max 7 character words, pick singular nouns over plurals, no words that start with an existing word, e.g. "find" and "finding".
 3. write this out as "initial_words.txt"
 4. filter this list to see if it's animal, vegetable, mineral, place, noun, adjective
 5. write this as "refined_words.txt"

2. put food_dishes_final at the top
3. put common_words at the top

## Now got words to use.

1. create 110,000 words with INVALID_POINT
2. Using the indices that are mapped to city center point radiuses.
  1. Fill the indices