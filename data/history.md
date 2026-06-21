
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

## v2 (current — 64,434 words)

The grid needs exactly 64,434 words (one per longitude bin), so v2 rebuilt the list to that exact
size and lives in `words/v2/`. See `words/v2/README.md` for the full pipeline.

- **`build_64434.py`** — regenerates the candidate pool from the v1 raw sources (Kaggle common
  words, food dishes, WordNet, Norvig) plus a hardcoded conversational/tech seed list. Applies the
  quality filter (3–8 letters, vowel, no stops/cities/profanity/acronyms) and strips plurals and
  inflected forms (`-ed/-ing/-er/-est/-ly`). Reference only — it writes `curated-rebuilt-64434.txt`
  and does not overwrite the hand-finalised `curated-by-chris-words.txt`.
- **`assign-conurb-words.py`** — reorders the base list so the commonest words sit on the grid
  indices covering the 5 biggest English conurbations (London, Manchester, West Midlands, West
  Yorkshire, Liverpool). Asserts the output is a true permutation of the input (no words lost).
- The prioritized output is copied to `/words.txt` and `/src/TwoWordsApi/words.txt`.

### Clean-up pass

- Removed redundant artifacts: a byte-identical duplicate of the base list, an orphaned
  intermediate ordering, and a stale PowerShell copy of the build script.
- Scrubbed NSFW and ephemeral meme slang (e.g. `gooning`, `coom`, `rizz`, `gyatt`, `skibidi`) that
  had been injected via the seed list, replacing them in place with neutral dictionary words so the
  count stayed at 64,434.
- Hardened `assign-conurb-words.py` so an overlap in conurbation indices can no longer drop words or
  emit a literal `"filler"` token.
- Made `build_64434.py` resolve its raw sources from `v1/` (with a `$TWOWORDS_SOURCES` override) so
  it runs from a clean checkout instead of crashing.