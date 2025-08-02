namespace TwoWordsApi.Services;

public interface IWordMappingService
{
    /// <summary>
    /// Gets the total number of words available
    /// </summary>
    int WordCount { get; }

    /// <summary>
    /// Gets words for given coordinates using GeoWordMapper
    /// </summary>
    (string LatitudeWord, string LongitudeWord) GetWords(double latitude, double longitude);

    /// <summary>
    /// Checks if coordinates are valid (words are not empty)
    /// </summary>
    bool IsValidCoordinate(double latitude, double longitude);

    /// <summary>
    /// Finds the index of a word in the word list (case insensitive)
    /// </summary>
    int FindWordIndex(string word);

    /// <summary>
    /// Gets coordinates from word pair
    /// </summary>
    (double Latitude, double Longitude)? GetCoordinatesFromWords(string latitudeWord, string longitudeWord);

    /// <summary>
    /// Gets statistics about the loaded polygon and word requirements
    /// </summary>
    (int RequiredWords, double Precision, string PolygonBounds) GetPolygonStatistics();

    /// <summary>
    /// Gets the polygon coordinates for rendering on maps
    /// </summary>
    List<List<(double Longitude, double Latitude)>> GetPolygonCoordinates();
}
