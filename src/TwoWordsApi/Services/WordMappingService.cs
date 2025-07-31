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
        // Convert indices back to coordinates for validation
        var lat = LatMin + (latIndex * Step);
        var lon = LonMin + (lonIndex * Step);

        // Check if either index is out of range
        if (latIndex >= _allWords.Length || lonIndex >= _allWords.Length)
            return false;

        // --- Begin precise UK land validation (ported from Python) ---
        // Core UK population rectangle
        bool inCore = (lat >= 50.7 && lat <= 54.0 && lon >= -4.5 && lon <= 1.8);
        if (inCore)
        {
            // Exclusions: major water bodies and mountains
            if (
                // Bristol Channel and Severn Estuary
                (lat >= 51.3 && lat <= 51.7 && lon >= -4.5 && lon <= -2.5) ||
                // The Wash (East England)
                (lat >= 52.7 && lat <= 53.1 && lon >= 0.0 && lon <= 0.8) ||
                // Thames Estuary (outer areas)
                (lat >= 51.3 && lat <= 51.6 && lon >= 0.5 && lon <= 1.8) ||
                // Exmoor/Dartmoor (Southwest highlands)
                (lat >= 50.7 && lat <= 51.3 && lon >= -4.5 && lon <= -3.3) ||
                // Peak District core (mountainous)
                (lat >= 53.1 && lat <= 53.5 && lon >= -2.0 && lon <= -1.5) ||
                // North Wales mountains (Snowdonia)
                (lat >= 52.7 && lat <= 53.2 && lon >= -4.1 && lon <= -3.6) ||
                // Lake District (too mountainous)
                (lat >= 54.3 && lat <= 54.8 && lon >= -3.4 && lon <= -2.9)
            )
            {
                return false;
            }
            return true;
        }

        // Outside core area - allow major cities only
        if (
            // Edinburgh (Scotland)
            (lat >= 55.9 && lat <= 56.0 && lon >= -3.3 && lon <= -3.1) ||
            // Glasgow (Scotland)
            (lat >= 55.8 && lat <= 55.9 && lon >= -4.4 && lon <= -4.1) ||
            // Newcastle/Sunderland corridor
            (lat >= 54.8 && lat <= 55.1 && lon >= -1.8 && lon <= -1.2) ||
            // Belfast area (Northern Ireland)
            (lat >= 54.5 && lat <= 54.7 && lon >= -6.0 && lon <= -5.8) ||
            // Plymouth (major southwest city)
            (lat >= 50.3 && lat <= 50.4 && lon >= -4.2 && lon <= -4.0) ||
            // Aberdeen (Scotland)
            (lat >= 57.1 && lat <= 57.2 && lon >= -2.2 && lon <= -2.0)
        )
        {
            return true;
        }

        return false;
        // --- End precise UK land validation ---
    }

    public int FindWordIndex(string word)
    {
        return Array.FindIndex(_allWords, w => w.Equals(word, StringComparison.OrdinalIgnoreCase));
    }
}
