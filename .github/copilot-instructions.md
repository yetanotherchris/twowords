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
- **Source**: `data/output/words.txt` contains the optimized 110,001 words
- **Optimization**: Food dishes prioritized for major population centers (see `data/python/optimize_word_list.py`)
- **Population mapping**: Indices 18224, 25073, 44808, etc. get memorable words like "pho", "basil", "kebab"
- **Land validation**: Built-in geographic filters exclude seas, mountains, remote areas

### Word List Source Information
- **Primary source**: Peter Norvig's curated English word list (norvig.com)
- **URL**: https://norvig.com/ngrams/word.list
- **Quality**: 263,533 high-quality English words, manually curated
- **Download location**: `data/words/norvig-word-list.txt` (main curated source)
- **Filtered to**: ~154,000 words after length and validation filtering
- **Benefits**: No non-English words (like "devaul", "cochao"), proper dictionary words only
- **Fallback**: Uses existing `data/output/words.txt` if Norvig list unavailable
- **Processing**: Direct access from `data/words` directory, clean and simple

### API Structure
The API has been refactored into a clean MVC architecture:

#### Controllers (`src/TwoWordsApi/Controllers/`)
- **TwoWordsController.cs**: Main API endpoints (words, validate, coordinates, examples, stats)
- **MapController.cs**: Interactive map visualization endpoint

#### Services (`src/TwoWordsApi/Services/`)
- **IWordMappingService.cs**: Interface for word mapping operations
- **WordMappingService.cs**: Core service handling word list loading and coordinate mapping
- **Dependency Injection**: Service registered as singleton in Program.cs for immediate initialization

#### Core Endpoints
```csharp
GET /words?lat=51.5&lon=-0.12     // Main mapping endpoint
GET /validate?lat=51.5&lon=-0.12  // Land validation
GET /coordinates?words=word1.word2 // Reverse mapping
GET /map?words=word1.word2        // Interactive map view
GET /examples                     // Sample cities/landmarks
GET /stats                        // System info
```

## Development Workflows

### Build & Test
```bash
# Standard .NET build from root directory
dotnet build twowords.sln -c Release
dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj

# Run API locally - IMPORTANT: Must run from src/TwoWordsApi directory
cd src/TwoWordsApi
dotnet run --urls http://localhost:5000

# Alternative: Run from root directory with project path
dotnet run --project src/TwoWordsApi/TwoWordsApi.csproj --urls http://localhost:5000

# COMMON MISTAKE: Do NOT run 'dotnet run' from root directory without specifying project
# This will fail with "Couldn't find a project to run"
```

### Word List Optimization
```bash
# From data/python/ directory - regenerate optimized word list
python optimize_word_list.py

# To redownload word sources (in data/words/ directory):
# Invoke-WebRequest -Uri "https://norvig.com/ngrams/word.list" -OutFile "data/words/norvig-word-list.txt"

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

-### Word Scoring Algorithm (`data/python/optimize_word_list.py`)
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
- `data/output/words.txt` - Optimized word list (110,001 entries)
- `data/words/norvig-word-list.txt` - Peter Norvig's curated English words (primary source)
- `data/words/important_indices.txt` - Population center indices for optimization
- `data/words/food_dishes_final.txt` - 163 food terms prioritized for cities
- `data/OPTIMIZATION_README.md` - Detailed optimization strategy and results

## External Dependencies
- **Minimal**: No database, no external APIs for validation
- **Deployment**: Single zip file contains all word data
- **Scaling**: Stateless design supports horizontal scaling

## Common Tasks



- Copilot must never prompt the user to continue or ask for permission to proceed.
- Copilot should always act until the user's problem is fully resolved, without unnecessary questions.
- Copilot should use available context and take direct action whenever possible.
