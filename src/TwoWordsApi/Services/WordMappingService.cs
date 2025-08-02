using System.IO.Compression;

namespace TwoWordsApi.Services;

public class WordMappingService : IWordMappingService
{
    private readonly GeoWordMapper _geoWordMapper;
    private readonly string[] _allWords;

    public int WordCount => _allWords.Length;

    public WordMappingService(IWebHostEnvironment environment, GeoWordMapper geoWordMapper)
    {
        _geoWordMapper = geoWordMapper;

        // Load words from zip file (same logic as before for consistency)
        string zipPath;
        var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";

        if (isInContainer)
        {
            zipPath = "/words.zip";
        }
        else
        {
            zipPath = Path.GetFullPath(Path.Combine(environment.ContentRootPath,
                "..", "..", "words.zip"));
        }

        // Verify the file exists
        if (!File.Exists(zipPath))
        {
            throw new FileNotFoundException($"words.zip not found at {zipPath}. " +
                $"ContentRootPath: {environment.ContentRootPath}, " +
                $"IsInContainer: {isInContainer}");
        }

        // Load words from zip file
        using var zip = ZipFile.OpenRead(zipPath);
        var wordsEntry = zip.Entries.FirstOrDefault(e => e.Name == "words.txt");
        if (wordsEntry == null)
        {
            throw new FileNotFoundException("words.txt not found in words.zip");
        }
        
        using var stream = wordsEntry.Open();
        using var reader = new StreamReader(stream);
        
        var words = new List<string>();
        string? line;
        while ((line = reader.ReadLine()) != null)
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
}
