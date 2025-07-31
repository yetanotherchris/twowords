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

}
