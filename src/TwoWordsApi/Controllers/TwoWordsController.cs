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

    [HttpGet("/stats")]
    [ProducesResponseType(typeof(string), 200)]
    public IActionResult GetStats()
    {
        var stats = $"Total words: {_wordMappingService.WordCount}\n" +
                    $"Latitude range: {_wordMappingService.LatMin} to {_wordMappingService.LatMax}\n" +
                    $"Longitude range: {_wordMappingService.LonMin} to {_wordMappingService.LonMax}\n" +
                    $"Step (precision): {_wordMappingService.Step}\n";

        return Ok(stats);
    }

    [HttpGet("/words")]
    [ProducesResponseType(typeof(string), 200)]
    [ProducesResponseType(400)]
    public IActionResult GetWords(
        [FromQuery] double lat, 
        [FromQuery] double lon)
    {
        if (lat < _wordMappingService.LatMin || lat > _wordMappingService.LatMax || 
            lon < _wordMappingService.LonMin || lon > _wordMappingService.LonMax)
        {
            return BadRequest("Coordinates out of range");
        }

        var latIndex = (int)Math.Floor((lat - _wordMappingService.LatMin) / _wordMappingService.Step);
        var lonIndex = (int)Math.Floor((lon - _wordMappingService.LonMin) / _wordMappingService.Step);

        if (latIndex >= _wordMappingService.LatCount || lonIndex >= _wordMappingService.LonCount)
        {
            return BadRequest("Word list is too small for these coordinates");
        }

        // Check if coordinates are valid using pre-computed validation
        if (!_wordMappingService.IsValidCoordinate(latIndex, lonIndex))
        {
            return BadRequest("Coordinates appear to be over water or inaccessible terrain");
        }

        var latitudeWord = _wordMappingService.GetWordAtIndex(latIndex);
        var longitudeWord = _wordMappingService.GetWordAtIndex(lonIndex);

        return Ok($"{latitudeWord}.{longitudeWord}");
    }

    [HttpGet("/validate")]
    [ProducesResponseType(typeof(object), 200)]
    public IActionResult ValidateCoordinates(
        [FromQuery] double lat, 
        [FromQuery] double lon)
    {
        if (lat < _wordMappingService.LatMin || lat > _wordMappingService.LatMax || 
            lon < _wordMappingService.LonMin || lon > _wordMappingService.LonMax)
        {
            return Ok(new { isValid = false, reason = "Out of range" });
        }

        var latIndex = (int)Math.Floor((lat - _wordMappingService.LatMin) / _wordMappingService.Step);
        var lonIndex = (int)Math.Floor((lon - _wordMappingService.LonMin) / _wordMappingService.Step);
        
        var isValid = _wordMappingService.IsValidCoordinate(latIndex, lonIndex);
        return Ok(new { 
            isValid = isValid, 
            reason = isValid ? "Valid land coordinates" : "Water or inaccessible terrain" 
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

        // Check if indices are within valid coordinate range
        if (latIndex >= _wordMappingService.LatCount)
        {
            return BadRequest($"Latitude word '{wordParts[0]}' corresponds to coordinates outside the supported range");
        }

        if (lonIndex >= _wordMappingService.LonCount)
        {
            return BadRequest($"Longitude word '{wordParts[1]}' corresponds to coordinates outside the supported range");
        }

        // Convert indices back to coordinates
        var lat = _wordMappingService.LatMin + (latIndex * _wordMappingService.Step);
        var lon = _wordMappingService.LonMin + (lonIndex * _wordMappingService.Step);

        // Validate that the coordinates are valid using pre-computed validation
        if (!_wordMappingService.IsValidCoordinate(latIndex, lonIndex))
        {
            return BadRequest("The coordinates for these words appear to be over water or inaccessible terrain");
        }

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
            if (city.Lat >= _wordMappingService.LatMin && city.Lat <= _wordMappingService.LatMax && 
                city.Lon >= _wordMappingService.LonMin && city.Lon <= _wordMappingService.LonMax)
            {
                var latIndex = (int)Math.Floor((city.Lat - _wordMappingService.LatMin) / _wordMappingService.Step);
                var lonIndex = (int)Math.Floor((city.Lon - _wordMappingService.LonMin) / _wordMappingService.Step);

                if (latIndex < _wordMappingService.LatCount && lonIndex < _wordMappingService.LonCount)
                {
                    var latWord = _wordMappingService.GetWordAtIndex(latIndex);
                    var lonWord = _wordMappingService.GetWordAtIndex(lonIndex);
                    examples.Add($"{city.Name} - {latWord}.{lonWord} ({city.Lon}, {city.Lat})");
                }
            }
        }

        // Process landmarks
        foreach (var landmark in landmarks)
        {
            if (landmark.Lat >= _wordMappingService.LatMin && landmark.Lat <= _wordMappingService.LatMax && 
                landmark.Lon >= _wordMappingService.LonMin && landmark.Lon <= _wordMappingService.LonMax)
            {
                var latIndex = (int)Math.Floor((landmark.Lat - _wordMappingService.LatMin) / _wordMappingService.Step);
                var lonIndex = (int)Math.Floor((landmark.Lon - _wordMappingService.LonMin) / _wordMappingService.Step);

                if (latIndex < _wordMappingService.LatCount && lonIndex < _wordMappingService.LonCount)
                {
                    var latWord = _wordMappingService.GetWordAtIndex(latIndex);
                    var lonWord = _wordMappingService.GetWordAtIndex(lonIndex);
                    examples.Add($"{landmark.Name} - {latWord} {lonWord} ({landmark.Lon}, {landmark.Lat})");
                }
            }
        }

        return Ok(examples);
    }
}
