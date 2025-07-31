# TwoWords Python Scripts

This directory contains Python scripts for optimizing and maintaining the TwoWords word lists.

## Active Scripts

### Core Word List Generation

- **`simple_fix_words.py`** - The current working script that generates the `geo_validated_words.zip` file used by the API. This ensures major UK cities get valid words while water coordinates are marked as "INVALID".

- **`create_optimized_geo_words.py`** - Advanced script with population-based optimization and enhanced UK land validation using hardcoded geographic rules.

- **`optimize_word_list.py`** - Strategic word placement script that prioritizes food dishes and common words for high-population areas using the curated Norvig word list.

### Supporting Scripts

- **`calculate_popular_indices.py`** - Calculates array indices for major UK population centres based on the coordinate-to-index mapping system.

- **`verify_indices.py`** - Validates that the coordinate-to-index calculations are working correctly for known locations.

## How the Word List System Works

The TwoWords API maps coordinates to words using a deterministic array lookup system:

1. **Coordinate Range**: UK/Ireland (49.0°-60.0°N, -8.0°-2.0°E) with 0.0001° steps (~10m precision)
2. **Index Calculation**: 
   - `latIndex = floor((lat - 49.0) / 0.0001)`
   - `lonIndex = floor((lon - (-8.0)) / 0.0001)`
3. **Array Size**: Exactly 110,001 words needed (covers max latitude index 110,000)
4. **Validation**: Invalid coordinates (water/non-UK) are marked as "INVALID" in the word list

## Current Implementation

The system currently uses `simple_fix_words.py` which:
- Loads words from `../word-data/norvig-word-list.txt` (Peter Norvig's curated English words)
- Applies simple UK land validation rules
- Ensures major cities (London, Manchester, Birmingham, etc.) get valid words
- Marks water coordinates and non-UK areas as "INVALID"
- Generates `geo_validated_words.zip` for the API to use

## Usage

### Regenerate the Word List

```bash
cd python
python simple_fix_words.py
```

This creates:
- `geo_validated_words.txt` - Text version of the word list
- `geo_validated_words.zip` - Compressed version used by the API

### Test the Generated List

```bash
cd python
python verify_indices.py
```

### Calculate New Population Indices

```bash
cd python
python calculate_popular_indices.py
```

## Output Files

- **`geo_validated_words.zip`** - Final word list used by the API (copy to project root)
- **`geo_validated_words.txt`** - Human-readable version of the word list
- **`optimized_words.txt`** - Output from the optimize_word_list.py script

## Dependencies

The active scripts use only built-in Python modules:
- `zipfile` - For creating compressed word lists
- `re` - For regex pattern matching
- `math` - For coordinate calculations
- `typing` - For type hints
- `dataclasses` - For data structures

No external dependencies are required. See `requirements.txt` for optional advanced features.

## Word List Strategy

### Current Approach (simple_fix_words.py)
- **Focus**: Ensure core functionality works reliably
- **Validation**: Simple geographic rules to exclude major water bodies
- **Word Quality**: Uses Peter Norvig's curated English word list
- **Population Bias**: Ensures major UK cities get valid words

### Advanced Approach (create_optimized_geo_words.py)  
- **Focus**: Population-based optimization with enhanced validation
- **Validation**: Detailed UK land validation with water body exclusions
- **Word Quality**: Multi-factor scoring (food dishes, common words, length, etc.)
- **Population Bias**: Strategic placement of best words at high-population indices

## Troubleshooting

### "loud.fart" Problem
If coordinates like Celtic Sea (51.0, -6.0) resolve to actual words instead of being rejected:
1. Run `simple_fix_words.py` to regenerate the word list
2. Copy the new `geo_validated_words.zip` to the project root
3. Restart the API

### Major Cities Not Working
If London, Manchester, or other major cities return "Coordinates appear to be over water":
1. Check that `simple_fix_words.py` is assigning words to the correct indices
2. Verify the coordinate-to-index calculation matches the API
3. Ensure the word list has valid words at those indices

### Word List Too Small
If you get "Word list is too small" errors:
1. Ensure the word list has exactly 110,001 entries
2. Check that `WORDS_NEEDED = 110001` in the script
3. Verify the zip file was created correctly

## File History

The python folder previously contained experimental scripts that have been cleaned up:
- `create_geo_validated_words*.py` - Early geographic validation attempts
- `enhanced_word_optimization.py` - Complex optimization experiments  
- `uk_geographic_validator.py` - Shapely-based validation (too complex)
- Various intermediate output files and boundary data

The current simplified approach proved more reliable and maintainable.
