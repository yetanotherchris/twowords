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
        var response = await _client.GetAsync("/words?lat=49.0&lon=-8.0");
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(json);
        Assert.Equal("a", doc.RootElement.GetProperty("latitudeWord").GetString());
        Assert.Equal("buzesi", doc.RootElement.GetProperty("longitudeWord").GetString());
    }

    [Fact]
    public async Task ReturnsBadRequestForOutOfRange()
    {
        var response = await _client.GetAsync("/words?lat=70&lon=0");
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

}
