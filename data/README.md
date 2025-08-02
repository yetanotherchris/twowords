
# TwoWords Data

This directory contains the data sources and word lists used by the TwoWords API.

## Current Status
The word list has been manually curated and is stored in `words/curated-by-chris-words.txt`. This file contains ~71,000 words from multiple sources including:

- Peter Norvig's word list (filtered for 3-8 characters, letters only)
- Common nouns and food dishes
- City names and first names
- WordNet nouns, adjectives, and verbs

## Key Files
- `words/curated-by-chris-words.txt` — Main curated word list (71,531 words)
- `words/norvig/` — Peter Norvig's original and filtered word lists
- `words/wordnet/` — WordNet-derived word lists
- `words/cities/` — City name lists
- `words/firstnames/` — First name lists
- `words/claude/` — Words curated by Claude

## Data Sources Evolution
See `history.md` for the complete evolution of data sources and curation methods.

## Notes
The main word list (`curated-by-chris-words.txt`) was manually created by combining and filtering words from multiple sources. Geographic filtering and coordinate mapping are handled by the API itself using the polygon data.
