# AI Agent Instructions for TwoWords

## Project Purpose
TwoWords maps UK/Ireland coordinates to two memorable words using a deterministic, stateless algorithm. The system consists of a .NET API that loads a pre-curated word list.

## Key Concepts
- **Stateless Mapping:** No database; all mapping is in-memory and deterministic.
- **Word List:** API loads `words.txt` at startup containing ~71,000 curated words.
- **Geographic Filtering:** Only land coordinates in the UK/Ireland polygon are valid.

## Directory Structure
- `src/TwoWordsApi/` — .NET API (controllers, services)
- `src/TwoWordsApi/words.txt` — Word list for API
- `data/words/curated-by-chris-words.txt` — Main curated word list (~71,531 words)
- `data/words/` — Various word source files (norvig, wordnet, cities, etc.)
- `tests/TwoWordsApi.Tests/` — xUnit API tests

## Developer Workflows
- **Run API:**
  - Docker: `docker-compose up -d`
  - .NET CLI: `dotnet build src/TwoWordsApi/TwoWordsApi.csproj -c Release && dotnet run --urls http://localhost:5000`
- **Update Word List:**
  - The main word list is `data/words/curated-by-chris-words.txt`
  - Copy this file to `src/TwoWordsApi/words.txt` for the API to use
- **Run Tests:**
  - `dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release`

## Data Sources
- Peter Norvig's word list, common nouns, food dishes, city names, first names, WordNet
- See `data/history.md` for sourcing evolution
- The main curated list was manually assembled from these sources

## Conventions
- All mapping is deterministic and reproducible
- API expects a single zipped word list at start-up
- Geographic validation uses polygon data in the API

For more, see `README.md` and `data/README.md`.
