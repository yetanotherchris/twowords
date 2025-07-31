# TwoWords API - Copilot Instructions

## Project Overview
TwoWords is a deterministic coordinate-to-word mapping service for the UK, similar to what3words but using only two words. It maps latitude/longitude coordinates to memorable word pairs via array index lookups.

## Core Architecture

### Coordinate Mapping System
- **Range**: UK/Ireland (49.0°-60.0°N, -8.0°-2.0°E) with 0.0001° steps (~10m precision)
- **Formula**: `latIndex = floor((lat - 49.0) / 0.0001)`, `lonIndex = floor((lon - (-8.0)) / 0.0001)`
- **Array size**: Exactly 110,001 words needed (covers max latitude index 110,000)
- **Stateless**: Same coordinates always return same words, no database required

### Word List Strategy
- **Source**: `expanded_words.zip` in root contains optimized 110,001 words
- **Optimization**: Food dishes prioritized for major population centers (see `python/optimize_word_list.py`)
- **Population mapping**: Indices 18224, 25073, 44808, etc. get memorable words like "pho", "basil", "kebab"
- **Land validation**: Built-in geographic filters exclude seas, mountains, remote areas

### Word List Source Information
- **Original source**: dwyl/english-words GitHub repository
- **URL**: https://github.com/dwyl/english-words
- **Download location**: `word-data/` folder (keeps all word files organized)
- **Final consolidated file**: `word-data/words_final.txt` (416,296 words)
- **Downloaded from**: https://raw.githubusercontent.com/dwyl/english-words/master/words.txt
- **Filtered with PowerShell**: `Get-Content word-data/words_comprehensive.txt | Where-Object { $_ -match "^[a-zA-Z]+$" }`
- **Removed 50,254 words** containing numbers, punctuation, or special characters
- **Preserves modern terms** (USB, email, internet, covid) and proper names (Deborah)

### API Structure (`src/TwoWordsApi/Program.cs`)
```csharp
// Core endpoints
GET /words?lat=51.5&lon=-0.12     // Main mapping endpoint
GET /validate?lat=51.5&lon=-0.12  // Land validation
GET /examples                     // Sample cities/landmarks
GET /stats                        // System info
```

## Development Workflows

### Build & Test
```bash
# Standard .NET build from root
dotnet build twowords.sln -c Release
dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj

# Run API locally
cd src/TwoWordsApi && dotnet run --urls http://localhost:5000
```

### Word List Optimization
```bash
# From python/ directory - regenerate optimized word list
python optimize_word_list.py

# Calculate population indices for new cities  
python calculate_popular_indices.py

# Verify mapping correctness
python verify_indices.py
```

## Key Project Patterns

### Geographic Validation
The `IsLikelyLand()` function uses hardcoded geographic rules rather than external services:
- Excludes Irish Sea, North Sea, English Channel by coordinate ranges
- Filters out Scottish Highlands, major lochs, remote islands
- Performance-critical: runs on every request without external calls

### Word Scoring Algorithm (`python/optimize_word_list.py`)
- **Food dishes**: +60 points (highest priority for population centers)
- **Short words (≤3 chars)**: +50 points
- **Common English words**: +40 points
- **Simple letter patterns**: +20 points
- Strategic placement ensures major cities get memorable words

### Testing Strategy
- Integration tests via `WebApplicationFactory<Program>` (see `tests/TwoWordsApi.Tests/`)
- Validates coordinate edge cases and land/water boundaries
- Tests assume specific word placements (first word is "a" at coordinates 49.0, -8.0)

## Critical Files
- `expanded_words.zip` - Optimized word list (110,001 entries)
- `word-data/important_indices.txt` - Population center indices for optimization
- `word-data/food_dishes_final.txt` - 163 food terms prioritized for cities
- `OPTIMIZATION_README.md` - Detailed optimization strategy and results

## External Dependencies
- **Minimal**: No database, no external APIs for validation
- **Deployment**: Single zip file contains all word data
- **Scaling**: Stateless design supports horizontal scaling

## Common Tasks
- **Add new city optimization**: Update `calculate_popular_indices.py`, regenerate word list
- **Adjust geographic boundaries**: Modify `IsLikelyLand()` rules in Program.cs
- **Change word prioritization**: Adjust scoring in `optimize_word_list.py`
- **API changes**: All logic in single Program.cs file using minimal APIs pattern
