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

```bash
# build
dotnet build TwoWordsApi/TwoWordsApi.csproj -c Release

# run
cd TwoWordsApi
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

Word data is loaded from the `geo_validated_words.zip` archive at the repository root. This file contains 110,001 entries with geographic validation to ensure only valid UK land coordinates resolve to actual words, while water areas and non-UK coordinates are marked as "INVALID".

### Word List Generation

The word list is generated using Python scripts in the `python/` directory:

1. **Source Data**: Uses Peter Norvig's curated English word list (word-data/norvig-word-list.txt) containing 263,533 high-quality English words
2. **Geographic Validation**: Applies UK land validation rules to exclude water bodies like Celtic Sea, North Sea, Thames Estuary, etc.
3. **Population Optimization**: Ensures major UK cities (London, Manchester, Birmingham) receive valid words while problematic coordinates are rejected
4. **Output**: Creates `geo_validated_words.zip` with exactly 110,001 words, where invalid coordinates contain "INVALID" markers

To regenerate the word list:
```bash
cd python
python simple_fix_words.py
```

See `python/README.md` for detailed documentation on the word list generation process.

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
1. Check the `geo_validated_words.zip` file is present in the project root
2. Regenerate the word list: `cd python && python simple_fix_words.py`
3. Copy the new zip file to the project root and restart the API

### Water Coordinates Resolving to Words

If coordinates over water (like Celtic Sea) are resolving to actual words instead of being rejected:
1. The word list needs regeneration with proper geographic validation
2. Run `cd python && python simple_fix_words.py` to fix this issue
3. Replace the old `geo_validated_words.zip` with the newly generated one

### Major Cities Not Working

If London, Manchester, or other major UK cities return validation errors:
1. Verify the word list contains valid words at the expected indices
2. Use `cd python && python verify_indices.py` to check the coordinate calculations
3. Regenerate the word list if needed

## Running tests

The solution includes a small xUnit test project. Run the tests with:

```bash
dotnet test TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
```
