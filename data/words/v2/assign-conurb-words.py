#!/usr/bin/env python3
"""
Properly assign commonest words to the grid indices covered by the 5 biggest English conurbations.

- Uses the real grid parameters from the GeoJSON (rounded 0.0001 deg bins).
- Computes per-conurbation the union of lat+lon bin indices inside rough bboxes.
- Allocates chunks of the "common" prefix (first 10k of the alpha v2 list) to chosen indices for each conurb.
- Builds a final word list where those specific indices get the common words.
- Produces:
  - conurbations/greater-london.txt etc. containing the words assigned to that area's chosen indices (in index order)
  - curated-by-chris-words-conurb-prioritized.txt : the full 64434 list with priority words at the right index slots, remaining spliced into the other slots.

This ensures that when word[i] is used for a lat or lon bin inside a big conurbation, it tends to be one of the commoner words.
"""
import json
import math
from pathlib import Path

BASE = Path(__file__).parent
STEP = 0.0001

# Grid constants (computed from central-uk.json)
MIN_LAT_R = 50.2379
MAX_LAT_R = 56.3304
MIN_LON_R = -4.7186
MAX_LON_R = 1.7247
NUM_LAT_BINS = 60926
NUM_LON_BINS = 64434
TOTAL_WORDS = 64434

def lat_index(lat: float) -> int:
    return int(round((round(lat, 5) - MIN_LAT_R) / STEP))

def lon_index(lon: float) -> int:
    return int(round((round(lon, 5) - MIN_LON_R) / STEP))

# Rough bboxes for the 5 biggest English conurbations (minlat, maxlat, minlon, maxlon)
CONURB_BBOXES = {
    "greater-london": (51.28, 51.70, -0.55, 0.35),
    "greater-manchester": (53.35, 53.65, -2.40, -2.05),
    "west-midlands": (52.35, 52.65, -2.05, -1.65),
    "west-yorkshire": (53.65, 53.95, -1.85, -1.35),
    "liverpool": (53.30, 53.50, -3.10, -2.75),
}

# Allocation of common words (from the first 10k of the alpha list)
# Order here determines priority for overlapping indices
CONURB_ALLOC = [
    ("greater-london", 2500),
    ("greater-manchester", 2000),
    ("west-midlands", 2000),
    ("west-yorkshire", 1750),
    ("liverpool", 1750),
]

def compute_indices_for_bbox(la0, la1, lo0, lo1):
    li0, li1 = lat_index(la0), lat_index(la1)
    lo0i, lo1i = lon_index(lo0), lon_index(lo1)
    lat_set = set(range(min(li0, li1), max(li0, li1) + 1))
    lon_set = set(range(min(lo0i, lo1i), max(lo0i, lo1i) + 1))
    # Clamp to valid
    lat_set = {i for i in lat_set if 0 <= i < NUM_LAT_BINS}
    lon_set = {i for i in lon_set if 0 <= i < NUM_LON_BINS}
    return sorted(lat_set | lon_set)

def main():
    # Load the base alpha v2 list (this is the "dictionary" order before geographic prioritization)
    base_list = [w.strip() for w in (BASE / "curated-by-chris-words.txt").read_text(encoding="utf-8").splitlines() if w.strip()]
    assert len(base_list) == TOTAL_WORDS, f"Expected {TOTAL_WORDS}, got {len(base_list)}"
    # Uniqueness is required for the permutation guarantee below (filtering a placed word would
    # otherwise drop every copy of it and run the filler short).
    assert len(set(base_list)) == len(base_list), "base list contains duplicate words"

    # The "commonest" pool is the first 10k in the current curation order
    common_pool = base_list[:10000]

    # Compute index sets
    conurb_indices = {}
    for name, (la0, la1, lo0, lo1) in CONURB_BBOXES.items():
        idxs = compute_indices_for_bbox(la0, la1, lo0, lo1)
        conurb_indices[name] = idxs
        print(f"{name}: {len(idxs)} candidate indices")

    # Assign common words to the lowest free index in each conurbation (ascending index order
    # for determinism). Process in CONURB_ALLOC order so London wins overlaps.
    #
    # A common word is consumed from common_pool ONLY when it is actually placed. This is what
    # keeps the result a true permutation of base_list: advancing a cursor by the full `alloc`
    # regardless of overlaps would skip (lose) common words and later run the filler short,
    # emitting the literal "filler" string. By draining a single iterator on placement, every
    # unconsumed common word simply stays in the pool and is spliced back in below.
    priority_assignments = {}  # index -> word
    per_conurb_words = {}
    common_iter = iter(common_pool)

    for name, alloc in CONURB_ALLOC:
        idxs = conurb_indices[name]
        words_here = []
        for i in idxs:
            if len(words_here) >= alloc:
                break
            if i in priority_assignments:
                # already claimed by an earlier (higher-priority) conurbation
                continue
            try:
                w = next(common_iter)
            except StopIteration:
                break  # common pool exhausted; remaining slots fall through to filler
            priority_assignments[i] = w
            words_here.append(w)
        per_conurb_words[name] = words_here
        print(f"  assigned {len(words_here)} common words to {name} (first index {idxs[0] if idxs else 'n/a'})")

    print(f"\nTotal priority slots filled: {len(priority_assignments)}")

    # Write the per-conurbation files (the common words for that area's chosen indices, in index order)
    conurb_dir = BASE / "conurbations"
    conurb_dir.mkdir(exist_ok=True)
    for name, words_for_area in per_conurb_words.items():
        out = conurb_dir / f"{name}.txt"
        out.write_text("\n".join(words_for_area) + "\n", encoding="utf-8")
        print(f"Wrote {out} ({len(words_for_area)} words)")

    # Build the final list: place priority words at their indices, splice every remaining word
    # (unconsumed common words first, then the rest of the pool) into the gaps in base order.
    # This is exactly base_list minus the placed words, so it always fills the gaps perfectly.
    result = [None] * TOTAL_WORDS
    for idx, w in priority_assignments.items():
        result[idx] = w

    placed = set(priority_assignments.values())
    filler = iter(w for w in base_list if w not in placed)
    for i in range(TOTAL_WORDS):
        if result[i] is None:
            result[i] = next(filler)

    # Guarantee the output is a true permutation of the input: no word dropped or duplicated.
    assert sorted(result) == sorted(base_list), "conurb prioritization is not a permutation of the base list"

    # Write the prioritized list
    out_main = BASE / "curated-by-chris-words-conurb-prioritized.txt"
    out_main.write_text("\n".join(result) + "\n", encoding="utf-8")
    print(f"\nWrote {out_main} (total {len(result)})")

    # Quick validation: show that some high-index London lon bins now have early common words
    # London's lon range ~41686-50686
    print("\nSample words now at London-ish high lon indices:")
    for sample in [42000, 45000, 48000]:
        if 0 <= sample < TOTAL_WORDS:
            print(f"  index {sample}: {result[sample]}")

    print("\nHead of the new list (low indices, which may be used by southern edges):")
    print(result[:8])

    print("\nDone. The prioritized list has common words placed at many of the indices covered by the 5 conurbations.")
    print("The per-conurb .txt files contain the subsets assigned to each.")

if __name__ == "__main__":
    main()
