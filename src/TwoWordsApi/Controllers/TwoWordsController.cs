using Microsoft.AspNetCore.Mvc;
using TwoWordsApi.Services;

namespace TwoWordsApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TwoWordsController : ControllerBase
{
    private readonly IWordMappingService _wordMappingService;

    public TwoWordsController(IWordMappingService wordMappingService)
    {
        _wordMappingService = wordMappingService;
    }

    // Shared logic for mapping coordinates to words (returns null if invalid)
    private string? MapCoordinatesToWords(double lat, double lon)
    {
        var (latWord, lonWord) = _wordMappingService.GetWords(lat, lon);
        
        if (string.IsNullOrEmpty(latWord) || string.IsNullOrEmpty(lonWord))
        {
            return null;
        }

        return $"{latWord}.{lonWord}";
    }

    [HttpGet("/stats")]
    [ProducesResponseType(typeof(string), 200)]
    public IActionResult GetStats()
    {
        var (requiredWords, precision, polygonBounds) = _wordMappingService.GetPolygonStatistics();
        
        var stats = $"Total words available: {_wordMappingService.WordCount:N0}\n" +
                    $"Words required for polygon: {requiredWords:N0}\n" +
                    $"Words sufficient: {(_wordMappingService.WordCount >= requiredWords ? "Yes" : "No")}\n" +
                    $"Coordinate precision: {precision} degrees (~{(precision * 111000):F0}m at equator)\n" +
                    $"Polygon bounds: {polygonBounds}\n" +
                    $"Using GeoWordMapper with polygon-based coordinate validation\n";

        return Ok(stats);
    }

    [HttpGet("/words")]
    [ProducesResponseType(typeof(string), 200)]
    [ProducesResponseType(400)]
    public IActionResult GetWords(
        [FromQuery] double lat, 
        [FromQuery] double lon)
    {
        var words = MapCoordinatesToWords(lat, lon);
        if (words == null)
        {
            return BadRequest("Coordinates are outside the loaded polygon");
        }
        return Ok(words);
    }

    [HttpGet("/validate")]
    [ProducesResponseType(typeof(object), 200)]
    public IActionResult ValidateCoordinates(
        [FromQuery] double lat, 
        [FromQuery] double lon)
    {
        var isValid = _wordMappingService.IsValidCoordinate(lat, lon);
        return Ok(new { 
            isValid = isValid, 
            reason = isValid ? "Valid coordinates within loaded polygon" : "Outside loaded polygon" 
        });
    }

    [HttpGet("/coordinates")]
    [ProducesResponseType(typeof(string), 200)]
    [ProducesResponseType(400)]
    public IActionResult GetCoordinates(
        [FromQuery] string words, 
        [FromQuery] string? format = "lat,lon")
    {
        // Parse the input format "word1.word2"
        var wordParts = words.Split('.');
        if (wordParts.Length != 2)
        {
            return BadRequest("Words must be in format 'word1.word2'");
        }

        var latitudeWord = wordParts[0].Trim();
        var longitudeWord = wordParts[1].Trim();

        // Find the indices of the words in the array
        var latIndex = _wordMappingService.FindWordIndex(latitudeWord);
        var lonIndex = _wordMappingService.FindWordIndex(longitudeWord);

        if (latIndex == -1)
        {
            return BadRequest($"Latitude word '{wordParts[0]}' not found in word list");
        }

        if (lonIndex == -1)
        {
            return BadRequest($"Longitude word '{wordParts[1]}' not found in word list");
        }

        // Try to get coordinates from words using the new method
        var coordinates = _wordMappingService.GetCoordinatesFromWords(latitudeWord, longitudeWord);
        
        if (coordinates == null)
        {
            return BadRequest("Unable to determine coordinates for these words. Reverse mapping functionality is not yet fully implemented.");
        }

        var (lat, lon) = coordinates.Value;

        // Format response based on the format parameter
        string response;
        if (format?.ToLower() == "lon,lat")
        {
            response = $"{lon:F4}, {lat:F4}";
        }
        else
        {
            response = $"{lat:F4}, {lon:F4}";
        }

        return Ok(response);
    }

    [HttpGet("/examples")]
    [ProducesResponseType(typeof(List<string>), 200)]
    public IActionResult GetExamples()
    {
        var examples = new List<string>();

        // Famous cities
        var cities = new[]
        {
            new { Name = "London", Lat = 51.5074, Lon = -0.1278 },
            new { Name = "Manchester", Lat = 53.4808, Lon = -2.2426 },
            new { Name = "Birmingham", Lat = 52.4862, Lon = -1.8904 },
            new { Name = "Bristol", Lat = 51.4545, Lon = -2.5879 },
            new { Name = "Liverpool", Lat = 53.4084, Lon = -2.9916 },
            new { Name = "Edinburgh", Lat = 55.9533, Lon = -3.1883 },
            new { Name = "Cardiff", Lat = 51.4816, Lon = -3.1791 }
        };

        // Famous landmarks
        var landmarks = new[]
        {
            new { Name = "Big Ben", Lat = 51.4994, Lon = -0.1245 },
            new { Name = "Glastonbury Festival Site", Lat = 51.1537, Lon = -2.5839 },
            new { Name = "Stonehenge", Lat = 51.1789, Lon = -1.8262 },
            new { Name = "Tower Bridge", Lat = 51.5055, Lon = -0.0754 },
            new { Name = "Windsor Castle", Lat = 51.4839, Lon = -0.6044 },
            new { Name = "Buckingham Palace", Lat = 51.5014, Lon = -0.1419 }
        };

        // Process cities
        foreach (var city in cities)
        {
            var words = MapCoordinatesToWords(city.Lat, city.Lon) ?? "INVALID";
            examples.Add($"{city.Name} - {words} ({city.Lon}, {city.Lat})");
        }

        // Process landmarks
        foreach (var landmark in landmarks)
        {
            var words = MapCoordinatesToWords(landmark.Lat, landmark.Lon) ?? "INVALID";
            examples.Add($"{landmark.Name} - {words} ({landmark.Lon}, {landmark.Lat})");
        }

        return Ok(examples);
    }
}
