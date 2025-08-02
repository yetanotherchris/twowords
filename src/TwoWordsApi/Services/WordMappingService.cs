using System;

namespace TwoWordsApi.Services;

public class WordMappingService : IWordMappingService
{
    private readonly GeoWordMapper _geoWordMapper;
    private readonly string[] _allWords;

    public int WordCount => _allWords.Length;

    public WordMappingService(IWebHostEnvironment environment, GeoWordMapper geoWordMapper)
    {
        _geoWordMapper = geoWordMapper;

        // Load words from text file
        string wordsPath;
        var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";

        if (isInContainer)
        {
            wordsPath = "/app/words.txt";
        }
        else
        {
            wordsPath = Path.Combine(environment.ContentRootPath, "words.txt");
        }

        // Verify the file exists
        if (!File.Exists(wordsPath))
        {
            throw new FileNotFoundException($"words.txt not found at {wordsPath}. " +
                $"ContentRootPath: {environment.ContentRootPath}, " +
                $"IsInContainer: {isInContainer}");
        }

        // Load words from text file
        var words = new List<string>();
        foreach (var line in File.ReadAllLines(wordsPath))
        {
            if (!string.IsNullOrWhiteSpace(line))
                words.Add(line.Trim());
        }
        _allWords = words.ToArray();
    }

    public (string LatitudeWord, string LongitudeWord) GetWords(double latitude, double longitude)
    {
        return _geoWordMapper.GetWords(latitude, longitude);
    }

    public bool IsValidCoordinate(double latitude, double longitude)
    {
        var (latWord, lonWord) = _geoWordMapper.GetWords(latitude, longitude);
        return !string.IsNullOrEmpty(latWord) && !string.IsNullOrEmpty(lonWord);
    }

    public int FindWordIndex(string word)
    {
        return Array.FindIndex(_allWords, w => w.Equals(word, StringComparison.OrdinalIgnoreCase));
    }

    public (double Latitude, double Longitude)? GetCoordinatesFromWords(string latitudeWord, string longitudeWord)
    {
        return _geoWordMapper.GetCoordinatesFromWords(latitudeWord, longitudeWord);
    }

    public (int RequiredWords, double Precision, string PolygonBounds) GetPolygonStatistics()
    {
        return _geoWordMapper.GetPolygonStatistics();
    }

    public List<List<(double Longitude, double Latitude)>> GetPolygonCoordinates()
    {
        return _geoWordMapper.GetPolygonCoordinates();
    }
}
