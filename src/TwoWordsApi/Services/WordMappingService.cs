using System.IO.Compression;

namespace TwoWordsApi.Services;

public class WordMappingService : IWordMappingService
{
    public const string InvalidLat = "INVALID_LAT";
    public const string InvalidLon = "INVALID_LON";
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
        // Determine the correct path for words.zip
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
        if (latIndex < 0 || latIndex >= LatCount || lonIndex < 0 || lonIndex >= LonCount)
            return false;

        var latWord = _allWords[latIndex];
        var lonWord = _allWords[lonIndex];

        return latWord != InvalidLat && lonWord != InvalidLon;
    }

    public int FindWordIndex(string word)
    {
        return Array.FindIndex(_allWords, w => w.Equals(word, StringComparison.OrdinalIgnoreCase));
    }
}
