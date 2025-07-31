# TwoWords Python Utilities

This directory contains a single script used to build the word list consumed by the API.

## generate_word_list.py

`generate_word_list.py` reads the UK polygon from `word-data/uk_polygon.wkt.zip` and the Norvig word list from `word-data/norvig-word-list.txt` in this directory. The polygon archive is not tracked in version control; if it is missing the script downloads the boundary from GitHub automatically. The script checks which latitude and longitude indices intersect the polygon using **Shapely** and writes `expanded_words.zip` to the repository root. Indices outside the polygon are filled with `INVALID_LAT` or `INVALID_LON`.

Run the script with:

```bash
cd python
python generate_word_list.py
```

The produced archive is ignored by Git.

To refresh the polygon data manually, run:

```bash
cd python
python download_uk_polygon.py
```
