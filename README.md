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

## Deterministic mapping

The service converts a coordinate to an index by rounding it to a 10&nbsp;m
grid. That index is used to look up a word in the respective list. As long as
  your word lists contain enough entries, each coordinate will always map to the
  same words without requiring a database or cache.

## Running tests

The solution includes a small xUnit test project. Run the tests with:

```bash
dotnet test TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
```
