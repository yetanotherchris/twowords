using System.Net;
using System.Net.Http;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace TwoWordsApi.Tests;

public class WordsEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public WordsEndpointTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task ReturnsWordPairForValidCoordinate()
    {
        // Use London coordinates which are guaranteed to be valid land
        var response = await _client.GetAsync("/words?lat=51.5074&lon=-0.1278");
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        
        // Should return a simple text response in format "word1.word2"
        Assert.Contains(".", content);
        Assert.DoesNotContain(" ", content.Trim());
    }

    [Fact]
    public async Task ReturnsBadRequestForOutOfRange()
    {
        var response = await _client.GetAsync("/words?lat=70&lon=0");
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task ReturnsBadRequestForWaterCoordinates()
    {
        // Test coordinates that are in range but over water
        var response = await _client.GetAsync("/words?lat=49.0&lon=-8.0");
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        
        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("water", content.ToLower());
    }

    [Fact]
    public async Task CoordinatesEndpoint_ReturnsValidCoordinatesForWordPair()
    {
        // First get words for a known coordinate
        var wordsResponse = await _client.GetAsync("/words?lat=51.5074&lon=-0.1278");
        wordsResponse.EnsureSuccessStatusCode();
        var wordPair = await wordsResponse.Content.ReadAsStringAsync();
        
        // Now use those words to get coordinates back
        var coordsResponse = await _client.GetAsync($"/coordinates?words={wordPair}");
        coordsResponse.EnsureSuccessStatusCode();
        var coordinates = await coordsResponse.Content.ReadAsStringAsync();
        
        // Should return coordinates in "lat, lon" format by default
        Assert.Contains(",", coordinates);
        var parts = coordinates.Split(',');
        Assert.Equal(2, parts.Length);
        
        // Verify coordinates are reasonable (close to London)
        var lat = double.Parse(parts[0].Trim());
        var lon = double.Parse(parts[1].Trim());
        Assert.InRange(lat, 51.0, 52.0);
        Assert.InRange(lon, -1.0, 0.0);
    }

    [Fact]
    public async Task CoordinatesEndpoint_ReturnsCoordinatesInLonLatFormat()
    {
        // First get words for a known coordinate
        var wordsResponse = await _client.GetAsync("/words?lat=51.5074&lon=-0.1278");
        wordsResponse.EnsureSuccessStatusCode();
        var wordPair = await wordsResponse.Content.ReadAsStringAsync();
        
        // Request coordinates in lon,lat format
        var coordsResponse = await _client.GetAsync($"/coordinates?words={wordPair}&format=lon,lat");
        coordsResponse.EnsureSuccessStatusCode();
        var coordinates = await coordsResponse.Content.ReadAsStringAsync();
        
        // Should return coordinates in "lon, lat" format
        Assert.Contains(",", coordinates);
        var parts = coordinates.Split(',');
        Assert.Equal(2, parts.Length);
        
        // Verify coordinates are reasonable (first should be longitude)
        var lon = double.Parse(parts[0].Trim());
        var lat = double.Parse(parts[1].Trim());
        Assert.InRange(lat, 51.0, 52.0);
        Assert.InRange(lon, -1.0, 0.0);
    }

    [Fact]
    public async Task CoordinatesEndpoint_ReturnsBadRequestForInvalidFormat()
    {
        var response = await _client.GetAsync("/coordinates?words=invalid");
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        
        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("word1.word2", content);
    }

    [Fact]
    public async Task CoordinatesEndpoint_ReturnsBadRequestForNonExistentWord()
    {
        var response = await _client.GetAsync("/coordinates?words=nonexistent.word");
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        
        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("not found", content);
    }

    [Fact]
    public async Task CoordinatesEndpoint_HandlesWordCase()
    {
        // First get words for a known coordinate
        var wordsResponse = await _client.GetAsync("/words?lat=51.5074&lon=-0.1278");
        wordsResponse.EnsureSuccessStatusCode();
        var wordPair = await wordsResponse.Content.ReadAsStringAsync();
        
        // Convert to uppercase and test
        var upperWordPair = wordPair.ToUpper();
        var coordsResponse = await _client.GetAsync($"/coordinates?words={upperWordPair}");
        coordsResponse.EnsureSuccessStatusCode();
        
        var coordinates = await coordsResponse.Content.ReadAsStringAsync();
        Assert.Contains(",", coordinates);
    }

}
