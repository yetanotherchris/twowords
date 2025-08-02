
# History

- Find word list – got an "alpha" list originally
- Map lat/lons of the boundaries of the UK to indices in a word list
- **Claude & Python:** Created lots of Python to try to clean this list of repeated words like "aal". Claude CoPilot went a bit over the top with looking for nouns, endings, and so on using code. Also created its own common word lists in Python.
- ChatGPT: asked to create nouns, food dishes

## Norvig

Remembered Peter Norvig's word list (via a Claude question). It had some issues with uncommon words.

- ChatGPT: Tried to merge the ChatGPT word lists in to make it a bit better
- Tried to restrict the list of words so any outside the UK mainland lat/lon would come back as "INVALID"

## Gaggle

Looked for a most popular words list in English, as dictionaries don't contain words like "wifi" or "London". Found a Gaggle one.

- Gaggle suffered from quality issues again

## WordNet

- Tried 2 versions of WordNet (settled with wn) to search for nouns, adjectives
- This didn't create enough words

## Firstnames Dataset

- GitHub Pickle file of name data
- Claude created a script to unpickle it
- Statistics about names, but it seemed wrong

## Cities Dataset

- GitHub CSV of cities
- Claude created a Python script to extract top UK city names as a text file

## Latest Refined Version

- Remove the Python as it's a mini operating system
- Norvig: creates a version of Norvig's list that is 3–8 characters long, letters only
- ChatGPT: produced 500 most popular first names
- WordNet: just provide text files of nouns, adjectives, verbs and filter for 3–8 chars (was only about 15k words)
- Store the dishes, common words in a claude folder
- Archived the Gaggle zip
- Archived the WordNet stuff
- Combined all of these text files into curated-by-chris-words.txt:
  - Dishes words
  - Cities words
  - Common words
  - Nouns
  - Norvig refined list
  - I manually mixed the above up via ChatGPT (and it did a bad job, with duplicates)

### Lat/lon to indices:
- Remove the city indices files and scripts
- Draw some polygons into GeoJson format and check if the latlons are in that