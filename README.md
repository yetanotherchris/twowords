# TwoWords: UK Geocoding with Two Words

TwoWords is a stateless geocoding system that maps UK/Ireland latitude and longitude coordinates to two memorable words, similar to what3words but using only two words. The project consists of a .NET API for serving word pairs and a Python-based data pipeline for generating the word lists.

## How It Works
- **Deterministic Mapping:** Each coordinate is mapped to a 10-meter grid. Latitude and longitude indices are mapped to words from a curated list.
- **No Database:** All mapping is in-memory and deterministic. The API loads a single `words.zip` file at startup.
- **Geographic Filtering:** Only coordinates within the UK/Ireland land polygon are valid. Out-of-bounds or water coordinates are rejected.

## Project Structure
- `src/TwoWordsApi/` — ASP.NET Core API (controllers, services, config)
- `data/` — Data pipeline scripts, word sources, and output files
- `data/words/curated-by-chris-words.txt` — Main curated word list
- `words.zip` — Zipped word list used by the API
- `tests/TwoWordsApi.Tests/` — xUnit test suite for API endpoints

## Running the API
**With Docker:**
```bash
docker-compose up -d
```
API will be available at http://localhost:8080

**With .NET CLI:**
```bash
dotnet build src/TwoWordsApi/TwoWordsApi.csproj -c Release
cd src/TwoWordsApi
dotnet run --urls http://localhost:5000
```

## Regenerating the Word List
See `data/README.md` for full details. In summary:
- Run the Python CLI (`twowords_cli.py`) to curate, filter, and zip the word list
- Place the resulting `words.zip` at the repo root for the API to use

## Testing
Run all API tests with:
```bash
dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
```

## Data Sources
- Peter Norvig's English word list
- Common nouns, food dishes, city names, and first names
- WordNet and Kaggle frequency data
- All sources are filtered, deduplicated, and combined into the final list

## More Information
- See `data/README.md` for pipeline and data details
- See `data/history.md` for project evolution and data sourcing
