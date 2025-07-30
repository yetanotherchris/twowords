# TwoWords Optimization: Popular Words for Major Conurbations

## Overview

This optimization enhances the TwoWords coordinate system by strategically placing the most popular English words at array indices corresponding to major UK conurbations and popular areas.

## What Was Done

### 1. Analysis Phase
- Analyzed the coordinate-to-index mapping system used by the TwoWords API
- Identified latitude/longitude ranges (49.0°-60.0°N, -8.0°-2.0°E) covering UK/Ireland
- Calculated specific array indices for major UK cities and popular areas
- Used step size of 0.0001 degrees (~10m precision)

### 2. Strategic Word Placement
- Selected the 300+ most common English words based on frequency
- Mapped 30 key indices corresponding to major conurbations:
  - **London** (9M population) → Index 25073: "**and**", Index 78722: "**an**"
  - **Manchester** (2.7M) → Index 44808: "**not**", Index 57574: "**this**"
  - **Birmingham** (2.9M) → Index 34861: "**in**", Index 61096: "**his**"
  - **Leeds** (1.9M) → Index 48008: "**on**", Index 64508: "**from**"
  - **Glasgow** (1.8M) → Index 68641: "**her**", Index 37481: "**that**"
  - And 10 other major cities...

### 3. Implementation
- Modified the existing `clean.py` script to create `clean_optimized.py`
- Preserved the original 1,040,000 word target size
- Maintained the mix of:
  - 370,105 real English words
  - 200,000 compound words
  - 469,895 generated pseudo-words
- Strategically displaced less important words to available positions

## Benefits

### User Experience
- **Memorable coordinates**: Major cities now use highly recognizable words
- **Easy communication**: "London is at and.an" vs "London is at analcite.bartisan"
- **Intuitive system**: Popular locations get popular words

### Technical Benefits
- **Full compatibility**: No changes to API structure or coordinate mapping
- **Complete coverage**: All 1,040,000 positions still covered
- **Balanced distribution**: Displaced words redistributed to maintain diversity

## Results

### Before Optimization
```
London      (51.5074, -0.1278)  → analcite.bartisan
Manchester  (53.4808, -2.2426)  → asynchronisms.autoiliadicful  
Birmingham  (52.4862, -1.8904)  → appendiculate.automcnabbing
```

### After Optimization
```
London      (51.5074, -0.1278)  → and.an
Manchester  (53.4808, -2.2426)  → not.this
Birmingham  (52.4862, -1.8904)  → in.his
```

## Files Modified

1. **`calculate_popular_indices.py`** - Calculates indices for major UK areas
2. **`clean_optimized.py`** - Enhanced version of clean.py with strategic placement
3. **`expanded_words.txt`** - Updated word list with optimal arrangement
4. **`expanded_words.zip`** - Compressed file used by the API
5. **`optimization_summary.py`** - Verification and demonstration script

## Technical Details

### Coordinate Mapping Formula
```
index = floor((coordinate - min_value) / step_size)
```

### Index Ranges
- **Latitude**: 0 to 110,000 (covering 49.0°N to 60.0°N)
- **Longitude**: 0 to 100,000 (covering -8.0°E to 2.0°E)

### Popular Words Used
The top 300+ most frequent English words including:
- Basic: the, be, to, of, and, a, in, that, have, it...
- Common: home, world, life, hand, part, child, eye...
- British: colour, favour, centre, theatre, programme...
- Simple: apple, bread, chair, dance, earth, fire...

## Usage

The optimization is automatically active when using the updated `expanded_words.zip` file. No changes are needed to the API code or client applications.

### Testing
```bash
# Test major cities
curl "http://localhost:5001/words?lat=51.5074&lon=-0.1278"  # London
curl "http://localhost:5001/words?lat=53.4808&lon=-2.2426"  # Manchester
curl "http://localhost:5001/words?lat=52.4862&lon=-1.8904"  # Birmingham
```

## Maintenance

To update the optimization with new popular areas:
1. Add coordinates to `calculate_popular_indices.py`
2. Run the script to get new indices
3. Update the popular words list in `clean_optimized.py` if needed
4. Regenerate the word list and zip file

This ensures the TwoWords system remains user-friendly while covering all coordinate requirements.
