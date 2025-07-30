# TwoWords API

This is a simple ASP.NET Core API that maps a latitude and longitude within
the UK to two deterministic words. The project is an example of how you could
build a vanity-style service similar to *what3words* but using only two words:
one representing latitude and one representing longitude.

The implementation here is intentionally small; the provided word lists only
contain a handful of entries. In a real deployment you would supply much larger
lists so that every 10&ndash;meter grid step in the UK can be uniquely
identified.

## Running

```bash
# build
dotnet build TwoWordsApi/TwoWordsApi.csproj -c Release

# run
cd TwoWordsApi
dotnet run --urls http://localhost:5000
```

Once running you can query the API using:

```
GET http://localhost:5000/words?lat=51.5&lon=-0.12
```

The response will look like:

```json
{"latitudeWord":"bravo","longitudeWord":"banana"}
```

## Word lists

Word data is loaded from the `expanded_words.zip` archive at the repository
root.  This file contains over a million entries.  On startup the service
unpacks the text file into a single list which is used for both latitude and
longitude indices.  The list is large enough to cover the entire UK at a
10&nbsp;m grid resolution.

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

## Running tests

The solution includes a small xUnit test project. Run the tests with:

```bash
dotnet test TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
```
