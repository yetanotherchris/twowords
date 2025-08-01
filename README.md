# TwoWords API

This is a simple ASP.NET Core API that maps a latitude and longitude within
the UK to two deterministic words. The project is an example of how you could
build a vanity-style service similar to *what3words* but using only two words:
one representing latitude and one representing longitude.

The implementation here is intentionally small; the provided word lists only
contain a handful of entries. In a real deployment you would supply much larger
lists so that every 10-meter grid step in the UK can be uniquely
identified.

## Running

### Using Docker (Recommended)

```bash
# Using Docker Compose
docker-compose up -d

# The API will be available at http://localhost:8080
```

### Using .NET directly

```bash
# build
dotnet build src/TwoWordsApi/TwoWordsApi.csproj -c Release

# run
cd src/TwoWordsApi
dotnet run --urls http://localhost:5000
```

> **Note**: The actual port may vary (often 5119 in development). Check the console output for the exact URL when the API starts.

Once running you can query the API using:

```
GET http://localhost:5000/words?lat=51.5&lon=-0.12
```

The response will look like:

```json
aah.aahed
```

For coordinates over water or outside the UK, the API will return an error:

```
GET http://localhost:5000/words?lat=51.0&lon=-6.0
```

```
Coordinates appear to be over water or inaccessible terrain
```

You can also validate coordinates without getting the words:

```
GET http://localhost:5000/validate?lat=51.5074&lon=-0.1278
```

```json
{"isValid":true,"reason":"Valid land coordinates"}
```

## Word lists

Word data is loaded from the `expanded_words.zip` archive at the repository root. This file contains curated words from multiple sources including Peter Norvig's English word list, food dishes, and common nouns. Invalid latitude or longitude indices are marked with placeholders so the API can reject out-of-bounds coordinates.

### Word List Generation

The word list is produced by the Python data pipeline in the `data/python/` directory:

1. **Source Data**: Multiple sources including Peter Norvig's English word list, common nouns, food dishes, and frequency data
2. **Geographic Validation**: Uses a UK/Ireland polygon to check which latitude and longitude indices intersect land
3. **Output**: Creates the final word list in `data/output/words.txt` and can generate `words.zip`

#### Using Docker (Recommended)

The easiest way to run the data pipeline is using Docker:

```bash
# Build the Python CLI image
docker build -f Dockerfile.python -t twowords-cli .

# Generate curated word list
docker run --rm twowords-cli python /python/twowords_cli.py curate

# Apply geographic filtering
docker run --rm twowords-cli python /python/twowords_cli.py filter

# Create compressed output
docker run --rm twowords-cli python /python/twowords_cli.py zip

# Copy the generated files from container to host (if needed)
docker run --rm -v $(pwd):/host twowords-cli cp /output/words.txt /words.zip /host/
```

#### Using Python directly

If you have Python 3.11+ and the required dependencies installed:

```bash
cd data/python
python twowords_cli.py curate      # Generate curated word list
python twowords_cli.py filter      # Apply geographic filtering
python twowords_cli.py zip         # Create words.zip from the output
```

Note: The API currently expects `expanded_words.zip` at the repository root. You may need to copy/rename the generated `words.zip` to `expanded_words.zip` for the API to function properly.

## Coordinate to Index Mapping

The service converts latitude and longitude coordinates to array indices using a deterministic algorithm. Each coordinate is mapped to a 10-meter grid resolution within the UK boundaries.

### Mapping Constants

```
Latitude Range:   49.0° to 60.0° (North)
Longitude Range:  -8.0° to 2.0° (East)
Step Size:        0.0001° (~10 meters)
```

### Index Calculation Formula

```
latIndex = floor((latitude - 49.0) / 0.0001)
lonIndex = floor((longitude - (-8.0)) / 0.0001)
```

### Example Mappings

```
┌─────────────────┬──────────┬───────────┬───────────┬────────────┐
│ Location        │ Latitude │ Longitude │ Lat Index │ Lon Index  │
├─────────────────┼──────────┼───────────┼───────────┼────────────┤
│ London          │  51.5074 │  -0.1278  │   25074   │    78720   │
│ Manchester      │  53.4808 │  -2.2426  │   44808   │    57574   │
│ Birmingham      │  52.4862 │  -1.8904  │   34862   │    61096   │
│ Edinburgh       │  55.9533 │  -3.1883  │   69533   │    48117   │
│ Cardiff         │  51.4816 │  -3.1791  │   24816   │    48209   │
│ Brighton        │  50.8225 │  -0.1372  │   18225   │    78628   │
│ Land's End      │  50.0661 │  -5.7132  │    6610   │    22868   │
│ John o' Groats  │  58.6440 │  -3.0702  │   96440   │    49298   │
└─────────────────┴──────────┴───────────┴───────────┴────────────┘
```

### Array Size Requirements

The number of indices required is calculated from the coordinate ranges and step size:

```
Latitude steps  = (60.0° - 49.0°) ÷ 0.0001° + 1 = 11.0° ÷ 0.0001° + 1 = 110,001
Longitude steps = (2.0° - (-8.0°)) ÷ 0.0001° + 1 = 10.0° ÷ 0.0001° + 1 = 100,001
```

This results in:

- **Latitude indices**: 0 to 110,000 (110,001 total)
- **Longitude indices**: 0 to 100,000 (100,001 total)
- **Word list size needed**: At least 110,001 words to cover all possible indices

The word list must contain enough entries to cover the highest possible index (110,000 for latitude), requiring a minimum of 110,001 words total.

### Deterministic Properties

As long as your word lists contain enough entries, each coordinate will always map to the same words without requiring a database or cache. The same coordinate will always produce:

1. The same latitude index → same latitude word
2. The same longitude index → same longitude word

This makes the service stateless and highly scalable.

## Troubleshooting

### Geographic Validation Issues

If coordinates that should be valid UK land are being rejected:
1. Check that the word list data is present
2. Regenerate the word list using Docker: 
   ```bash
   docker run --rm twowords-cli python /python/twowords_cli.py curate
   docker run --rm twowords-cli python /python/twowords_cli.py filter
   ```
3. Restart the API

### Water Coordinates Resolving to Words

If coordinates over water (like Celtic Sea) are resolving to actual words instead of being rejected:
1. The word list needs regeneration with proper geographic validation
2. Run the filter command using Docker:
   ```bash
   docker run --rm twowords-cli python /python/twowords_cli.py filter
   ```
3. Restart the API with the updated word list

### Major Cities Not Working

If London, Manchester, or other major UK cities return validation errors:
1. Verify the word list contains valid words at the expected indices
2. Regenerate the word list using Docker:
   ```bash
   docker run --rm twowords-cli python /python/twowords_cli.py curate
   docker run --rm twowords-cli python /python/twowords_cli.py filter
   ```

## Running tests

The solution includes a small xUnit test project. Run the tests with:

```bash
dotnet test TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
```
