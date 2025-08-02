using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace TwoWordsApi.Services;

public class GeoWordMapper
{
    private readonly List<string> _words;
    private readonly List<List<(double Longitude, double Latitude)>> _polygons;
    private readonly double _minLatitude;
    private readonly double _maxLatitude;
    private readonly double _minLongitude;
    private readonly double _maxLongitude;
    private readonly double _minLatitudeRounded;
    private readonly double _maxLatitudeRounded;
    private readonly double _minLongitudeRounded;
    private readonly double _maxLongitudeRounded;
    private readonly int _numLatitudeBins;
    private readonly int _numLongitudeBins;
    private readonly double _step = 0.0001;

    public GeoWordMapper(string geoJsonPath, string wordListPath)
    {
        // Read word list
        _words = File.ReadAllLines(wordListPath).ToList();

        // Read and parse GeoJSON
        string geoJsonText = File.ReadAllText(geoJsonPath);
        using JsonDocument doc = JsonDocument.Parse(geoJsonText);

        List<List<(double Longitude, double Latitude)>> polygons = new List<List<(double Longitude, double Latitude)>>();
        string rootType = doc.RootElement.GetProperty("type").GetString() ?? 
            throw new ArgumentException("Invalid GeoJSON: missing or null type property");

        if (rootType == "FeatureCollection")
        {
            var features = doc.RootElement.GetProperty("features").EnumerateArray();
            foreach (var feature in features)
            {
                AddPolygonFromGeometry(feature.GetProperty("geometry"), polygons);
            }
        }
        else if (rootType == "Feature")
        {
            AddPolygonFromGeometry(doc.RootElement.GetProperty("geometry"), polygons);
        }
        else if (rootType == "Polygon")
        {
            AddPolygonFromGeometry(doc.RootElement, polygons);
        }
        else
        {
            throw new ArgumentException("Unsupported GeoJSON type. Supports Polygon, Feature with Polygon, or FeatureCollection with Polygon features.");
        }

        if (polygons.Count == 0)
        {
            throw new ArgumentException("No valid Polygons found in GeoJSON.");
        }

        _polygons = polygons;

        // Calculate min/max across all points
        var allPoints = polygons.SelectMany(p => p);
        _minLatitude = allPoints.Min(p => p.Latitude);
        _maxLatitude = allPoints.Max(p => p.Latitude);
        _minLongitude = allPoints.Min(p => p.Longitude);
        _maxLongitude = allPoints.Max(p => p.Longitude);

        // Round min/max to nearest step boundaries
        _minLatitudeRounded = Math.Floor(_minLatitude / _step) * _step;
        _maxLatitudeRounded = Math.Ceiling(_maxLatitude / _step) * _step;
        _minLongitudeRounded = Math.Floor(_minLongitude / _step) * _step;
        _maxLongitudeRounded = Math.Ceiling(_maxLongitude / _step) * _step;

        // Calculate number of bins
        _numLatitudeBins = (int)Math.Round((_maxLatitudeRounded - _minLatitudeRounded) / _step) + 1;
        _numLongitudeBins = (int)Math.Round((_maxLongitudeRounded - _minLongitudeRounded) / _step) + 1;

        // Assume enough words (as per requirements); check for the larger dimension
        int requiredWords = Math.Max(_numLatitudeBins, _numLongitudeBins);
        if (_words.Count < requiredWords)
        {
            throw new InvalidOperationException("Not enough words in the list for the polygon's latitude and longitude ranges.");
        }
    }

    private void AddPolygonFromGeometry(JsonElement geometryElement, List<List<(double Longitude, double Latitude)>> polygons)
    {
        if (geometryElement.GetProperty("type").GetString() == "Polygon")
        {
            // Assume simple polygon without holes; take exterior ring
            var exteriorRing = geometryElement.GetProperty("coordinates").EnumerateArray().First().EnumerateArray();
            var points = new List<(double Longitude, double Latitude)>();
            foreach (var coord in exteriorRing)
            {
                var coordArray = coord.EnumerateArray();
                var enumerator = coordArray.GetEnumerator();
                enumerator.MoveNext();
                double lon = enumerator.Current.GetDouble();
                enumerator.MoveNext();
                double lat = enumerator.Current.GetDouble();
                points.Add((lon, lat));
            }
            polygons.Add(points);
        }
    }

    public (string LatitudeWord, string LongitudeWord) GetWords(double latitude, double longitude)
    {
        // Check if point is inside any polygon
        if (!IsPointInAnyPolygon(longitude, latitude))
        {
            return ("", "");
        }

        // Round to 5 decimal places
        double roundedLatitude = Math.Round(latitude, 5);
        double roundedLongitude = Math.Round(longitude, 5);

        // Calculate indices
        int latitudeIndex = (int)Math.Round((roundedLatitude - _minLatitudeRounded) / _step);
        int longitudeIndex = (int)Math.Round((roundedLongitude - _minLongitudeRounded) / _step);

        // Check indices
        if (latitudeIndex < 0 || latitudeIndex >= _numLatitudeBins || longitudeIndex < 0 || longitudeIndex >= _numLongitudeBins)
        {
            return ("", "");
        }

        // Assign words
        string latitudeWord = _words[latitudeIndex];
        string longitudeWord = _words[longitudeIndex];

        return (latitudeWord, longitudeWord);
    }

    public (double Latitude, double Longitude)? GetCoordinatesFromWords(string latitudeWord, string longitudeWord)
    {
        // Find the indices of the words
        int latitudeIndex = _words.IndexOf(latitudeWord);
        int longitudeIndex = _words.IndexOf(longitudeWord);

        if (latitudeIndex == -1 || longitudeIndex == -1)
        {
            return null;
        }

        // Check if indices are within valid bounds
        if (latitudeIndex >= _numLatitudeBins || longitudeIndex >= _numLongitudeBins)
        {
            return null;
        }

        // Convert indices back to coordinates
        double latitude = _minLatitudeRounded + (latitudeIndex * _step);
        double longitude = _minLongitudeRounded + (longitudeIndex * _step);

        // Verify the coordinates are within polygon (optional validation)
        if (!IsPointInAnyPolygon(longitude, latitude))
        {
            return null;
        }

        return (latitude, longitude);
    }

    public (int RequiredWords, double Precision, string PolygonBounds) GetPolygonStatistics()
    {
        var precision = _step;
        var requiredWords = Math.Max(_numLatitudeBins, _numLongitudeBins);
        var bounds = $"Lat: {_minLatitude:F6} to {_maxLatitude:F6}, Lon: {_minLongitude:F6} to {_maxLongitude:F6}";
        
        return (requiredWords, precision, bounds);
    }

    public int GetRequiredWordCount(int precision = 5)
    {
        if (precision < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(precision), "Precision must be non-negative.");
        }

        double step = Math.Pow(10, -precision);

        double minLatRounded = Math.Floor(_minLatitude / step) * step;
        double maxLatRounded = Math.Ceiling(_maxLatitude / step) * step;
        int numLatBins = (int)Math.Round((maxLatRounded - minLatRounded) / step) + 1;

        double minLonRounded = Math.Floor(_minLongitude / step) * step;
        double maxLonRounded = Math.Ceiling(_maxLongitude / step) * step;
        int numLonBins = (int)Math.Round((maxLonRounded - minLonRounded) / step) + 1;

        return Math.Max(numLatBins, numLonBins);
    }

    private bool IsPointInAnyPolygon(double x, double y)
    {
        foreach (var polygonPoints in _polygons)
        {
            bool inside = false;
            int n = polygonPoints.Count;
            for (int i = 0, j = n - 1; i < n; j = i++)
            {
                var pi = polygonPoints[i];
                var pj = polygonPoints[j];
                if ((pi.Latitude > y) != (pj.Latitude > y) &&
                    x < pj.Longitude + (pi.Longitude - pj.Longitude) * (y - pj.Latitude) / (pi.Latitude - pj.Latitude))
                {
                    inside = !inside;
                }
            }
            if (inside)
            {
                return true;
            }
        }
        return false;
    }
}