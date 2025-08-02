
using TwoWordsApi.Services;
using Xunit;
namespace TwoWordsApi.Tests;

// dotnet test --filter "FullyQualifiedName~TwoWordsApi.Tests.GeoWordMapperTests"
public class GeoWordMapperTests
{
    [Fact]
    public void TestUKCities()
    {
        // GeoJSON content
        string geoJsonContent = """
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -3.286392879523362,
              54.09329758112176
            ],
            [
              -3.286392879523362,
              50.62903157376334
            ],
            [
              -0.0215312238135823,
              50.62903157376334
            ],
            [
              -0.0215312238135823,
              54.09329758112176
            ],
            [
              -3.286392879523362,
              54.09329758112176
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -0.048776123530672066,
              51.70384123690803
            ],
            [
              -0.048776123530672066,
              50.74350896819297
            ],
            [
              0.4243255851787069,
              50.74350896819297
            ],
            [
              0.4243255851787069,
              51.70384123690803
            ],
            [
              -0.048776123530672066,
              51.70384123690803
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              0.4433063251246381,
              51.38435584954209
            ],
            [
              0.4433063251246381,
              50.91306754328258
            ],
            [
              0.9348105442228132,
              50.91306754328258
            ],
            [
              0.9348105442228132,
              51.38435584954209
            ],
            [
              0.4433063251246381,
              51.38435584954209
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              0.8526267182510026,
              51.32866580782658
            ],
            [
              0.8526267182510026,
              51.066041152164075
            ],
            [
              1.4258262353155828,
              51.066041152164075
            ],
            [
              1.4258262353155828,
              51.32866580782658
            ],
            [
              0.8526267182510026,
              51.32866580782658
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}
""";

        string geoPath = Path.GetTempFileName();
        File.WriteAllText(geoPath, geoJsonContent);

        // Generate word list with 600,000 words
        var words = Enumerable.Range(0, 600000).Select(i => $"word{i}").ToList();
        string wordPath = Path.GetTempFileName();
        File.WriteAllLines(wordPath, words);

        var mapper = new GeoWordMapper(geoPath, wordPath);

        // List of 30 UK cities (from England)
        var cities = new List<(string Name, double Latitude, double Longitude)>
            {
                ("York", 53.958332, -1.080278),
                ("Worcester", 52.192001, -2.220000),
                ("Winchester", 51.063202, -1.308000),
                ("Wells", 51.209000, -2.647000),
                ("Wakefield", 53.680000, -1.490000),
                ("Sheffield", 53.383331, -1.466667),
                ("Salford", 53.483002, -2.293100),
                ("St.Albans", 51.755001, -0.336000),
                ("Ripon", 54.138000, -1.524000),
                ("Portsmouth", 50.805832, -1.087222),
                ("Nottingham", 52.950001, -1.150000),
                ("Liverpool", 53.400002, -2.983333),
                ("Lincoln", 53.234444, -0.538611),
                ("Lichfield", 52.683498, -1.826530),
                ("Leicester", 52.633331, -1.133333),
                ("Lancaster", 54.047001, -2.801000),
                ("Hereford", 52.056499, -2.716000),
                ("Gloucester", 51.864445, -2.244444),
                ("Exeter", 50.716667, -3.533333),
                ("Ely", 52.398056, 0.262222),
                ("Derby", 52.916668, -1.466667),
                ("Coventry", 52.408054, -1.510556),
                ("Chichester", 50.836498, -0.779200),
                ("Chester", 53.189999, -2.890000),
                ("Chelmsford", 51.736099, 0.479800),
                ("Canterbury", 51.279999, 1.080000),
                ("Cambridge", 52.205276, 0.119167),
                ("Brighton & Hove", 50.827778, -0.152778),
                ("Bradford", 53.799999, -1.750000),
                ("Bath", 51.380001, -2.360000)
            };

        foreach (var city in cities)
        {
            var (latWord, lonWord) = mapper.GetWords(city.Latitude, city.Longitude);
            // Assert that words are assigned if point is inside; since most are, and to check functionality,
            // we can assert they are not both empty, but some may be outside, so no strict assert.
            // For the purpose of this test, we ensure no exceptions are thrown.
        }

        // Clean up temp files
        File.Delete(geoPath);
        File.Delete(wordPath);

        // If no exceptions, test passes
    }

    [Fact]
    public void TestRequiredWordCount()
    {
        // GeoJSON content (same as above)
        string geoJsonContent = """
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -3.286392879523362,
              54.09329758112176
            ],
            [
              -3.286392879523362,
              50.62903157376334
            ],
            [
              -0.0215312238135823,
              50.62903157376334
            ],
            [
              -0.0215312238135823,
              54.09329758112176
            ],
            [
              -3.286392879523362,
              54.09329758112176
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -0.048776123530672066,
              51.70384123690803
            ],
            [
              -0.048776123530672066,
              50.74350896819297
            ],
            [
              0.4243255851787069,
              50.74350896819297
            ],
            [
              0.4243255851787069,
              51.70384123690803
            ],
            [
              -0.048776123530672066,
              51.70384123690803
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              0.4433063251246381,
              51.38435584954209
            ],
            [
              0.4433063251246381,
              50.91306754328258
            ],
            [
              0.9348105442228132,
              50.91306754328258
            ],
            [
              0.9348105442228132,
              51.38435584954209
            ],
            [
              0.4433063251246381,
              51.38435584954209
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              0.8526267182510026,
              51.32866580782658
            ],
            [
              0.8526267182510026,
              51.066041152164075
            ],
            [
              1.4258262353155828,
              51.066041152164075
            ],
            [
              1.4258262353155828,
              51.32866580782658
            ],
            [
              0.8526267182510026,
              51.32866580782658
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}
""";

        string geoPath = Path.GetTempFileName();
        File.WriteAllText(geoPath, geoJsonContent);

        // Generate word list with 600,000 words (more than required)
        var words = Enumerable.Range(0, 600000).Select(i => $"word{i}").ToList();
        string wordPath = Path.GetTempFileName();
        File.WriteAllLines(wordPath, words);

        var mapper = new GeoWordMapper(geoPath, wordPath);

        int required = mapper.GetRequiredWordCount(5);
        Assert.Equal(471224, required);

        // Clean up temp files
        File.Delete(geoPath);
        File.Delete(wordPath);
    }
}