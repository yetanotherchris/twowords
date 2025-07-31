using System.IO.Compression;

namespace TwoWordsApi.Services;

public class WordMappingService : IWordMappingService
{
    private readonly string[] _allWords;

    public double LatMin { get; } = 49.0;
    public double LatMax { get; } = 60.0;
    public double LonMin { get; } = -8.0;
    public double LonMax { get; } = 2.0;
    public double Step { get; } = 0.0001; // ~10m

    public int LatCount { get; }
    public int LonCount { get; }
    public int WordCount => _allWords.Length;

    public WordMappingService(IWebHostEnvironment environment)
    {
        // Determine the correct path for expanded_words.zip
        string zipPath;
        var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";

        if (isInContainer)
        {
            zipPath = "/expanded_words.zip";
        }
        else
        {
            zipPath = Path.GetFullPath(Path.Combine(environment.ContentRootPath,
                "..", "..", "expanded_words.zip"));
        }

        // Verify the file exists
        if (!File.Exists(zipPath))
        {
            throw new FileNotFoundException($"expanded_words.zip not found at {zipPath}. " +
                $"ContentRootPath: {environment.ContentRootPath}, " +
                $"IsInContainer: {isInContainer}");
        }

        // Load words from zip file
        using var zip = ZipFile.OpenRead(zipPath);
        using var stream = zip.Entries.First().Open();
        using var reader = new StreamReader(stream);
        
        var words = new List<string>();
        string? line;
        while ((line = reader.ReadLine()) != null)
        {
            if (!string.IsNullOrWhiteSpace(line))
                words.Add(line.Trim());
        }
        _allWords = words.ToArray();

        // Calculate coordinate counts
        LatCount = (int)Math.Ceiling((LatMax - LatMin) / Step) + 1;
        LonCount = (int)Math.Ceiling((LonMax - LonMin) / Step) + 1;

        // Validate word list size
        if (_allWords.Length < Math.Max(LatCount, LonCount))
            throw new Exception("Word list is not large enough for coverage.");
    }

    public string GetWordAtIndex(int index)
    {
        if (index < 0 || index >= _allWords.Length)
            throw new ArgumentOutOfRangeException(nameof(index));
        
        return _allWords[index];
    }

    public bool IsValidCoordinate(int latIndex, int lonIndex)
    {
        // Since we're using expanded_words.zip, we can do basic geographic validation
        // Convert indices back to coordinates for validation
        var lat = LatMin + (latIndex * Step);
        var lon = LonMin + (lonIndex * Step);
        
        // Check if either index is out of range
        if (latIndex >= _allWords.Length || lonIndex >= _allWords.Length)
            return false;
        
        // Basic geographic validation for UK/Ireland region
        // Exclude obvious water areas (simplified validation)
        
        // Irish Sea (rough boundaries)
        if (lat >= 53.0 && lat <= 55.0 && lon >= -6.0 && lon <= -3.0)
            return false;
            
        // English Channel (rough boundaries)  
        if (lat >= 49.0 && lat <= 51.0 && lon >= -2.0 && lon <= 2.0)
            return false;
            
        // North Sea (rough boundaries)
        if (lat >= 54.0 && lat <= 60.0 && lon >= 0.0 && lon <= 2.0)
            return false;
        
        return true;
    }

    public int FindWordIndex(string word)
    {
        return Array.FindIndex(_allWords, w => w.Equals(word, StringComparison.OrdinalIgnoreCase));
    }
}
