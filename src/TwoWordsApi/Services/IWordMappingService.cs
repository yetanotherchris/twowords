namespace TwoWordsApi.Services;

public interface IWordMappingService
{
    /// <summary>
    /// Gets the word at the specified index
    /// </summary>
    string GetWordAtIndex(int index);

    /// <summary>
    /// Gets the total number of words available
    /// </summary>
    int WordCount { get; }

    /// <summary>
    /// Checks if coordinates are valid (not marked as INVALID)
    /// </summary>
    bool IsValidCoordinate(int latIndex, int lonIndex);

    /// <summary>
    /// Finds the index of a word in the word list (case insensitive)
    /// </summary>
    int FindWordIndex(string word);

    /// <summary>
    /// Geographic constants for coordinate mapping
    /// </summary>
    double LatMin { get; }
    double LatMax { get; }
    double LonMin { get; }
    double LonMax { get; }
    double Step { get; }
    int LatCount { get; }
    int LonCount { get; }
}
