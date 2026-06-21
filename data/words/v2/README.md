# TwoWords word list — v2 (64,434 words)

This is the current word list used by the API. The list has exactly **64,434 words** — one per
longitude bin of the central-UK grid (see `central-uk.json`) — so every valid coordinate maps to a
unique `word1.word2` pair.

## Files

| File | Role |
| --- | --- |
| `curated-by-chris-words.txt` | **Source of truth.** The 64,434-word base list in curation order (priority block first). Hand-finalised, so it is committed directly. |
| `assign-conurb-words.py` | Reorders the base list so the commonest words land on grid indices covering the 5 biggest English conurbations. Produces the prioritized list + per-conurbation files. |
| `curated-by-chris-words-conurb-prioritized.txt` | Output of the script above — the **shipped** ordering. Copied verbatim to `/words.txt` and `/src/TwoWordsApi/words.txt`. |
| `conurbations/*.txt` | The common words assigned to each conurbation's indices (London, Manchester, West Midlands, West Yorkshire, Liverpool), in index order. |
| `build_64434.py` | Reference generator that rebuilds the candidate pool from the raw sources. Writes `curated-rebuilt-64434.txt` (gitignored) — it does **not** overwrite the curated base. |
| `wikipedia/extract-wiki-common.ps1` | Optional helper to derive a common-word list from a Wikipedia word-frequency dump. |

## Pipeline

```
raw sources (data/words/v1/*)
        │  build_64434.py          (filter + dedup; reference only)
        ▼
curated-by-chris-words.txt          ← committed source of truth (hand-finalised)
        │  assign-conurb-words.py
        ▼
curated-by-chris-words-conurb-prioritized.txt
        │  copy
        ▼
/words.txt  and  /src/TwoWordsApi/words.txt   ← read by the API
```

### Regenerating the shipped list

After editing `curated-by-chris-words.txt`:

```sh
cd data/words/v2
python assign-conurb-words.py
cp curated-by-chris-words-conurb-prioritized.txt ../../../words.txt
cp curated-by-chris-words-conurb-prioritized.txt ../../../src/TwoWordsApi/words.txt
```

`assign-conurb-words.py` asserts the output is a true permutation of the base list, so no word is
ever dropped or duplicated and the count stays at 64,434.

### Re-running the generator (optional)

`build_64434.py` resolves its raw sources from `$TWOWORDS_SOURCES`, then `v2/`, then `v1/`, so it
runs from a clean checkout without the source folders being copied into `v2/`. It writes
`curated-rebuilt-64434.txt` for comparison only.

## Quality rules

Each word is 3–8 lowercase `a–z` letters with at least one vowel, and is excluded if it is a stop
word, a UK/world city name, profanity, or a common acronym. Plurals and inflected forms (`-s/-es/-ies/-ves`,
`-ed/-ing/-er/-est/-ly`, irregular plurals) are dropped when the base form is present. NSFW and
ephemeral meme slang are kept out of the conversational/tech seed list (`conv_raw` in `build_64434.py`).
