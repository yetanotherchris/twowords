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

The `data/` directory contains two example files:

- `lat_words.txt` &ndash; words representing latitude
- `lon_words.txt` &ndash; words representing longitude

Each line is a single word. The sample lists are tiny; for true rooftop
accuracy (about 10&nbsp;m) across the UK you would need on the order of
100,000 unique words for latitude and about 70,000 for longitude.

## Deterministic mapping

The service converts a coordinate to an index by rounding it to a 10&nbsp;m
grid. That index is used to look up a word in the respective list. As long as
your word lists contain enough entries, each coordinate will always map to the
same words without requiring a database or cache.
