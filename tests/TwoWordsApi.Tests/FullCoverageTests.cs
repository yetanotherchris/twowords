using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using TwoWordsApi.Services;
using Xunit;

namespace TwoWordsApi.Tests;

public class FullCoverageTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly IWordMappingService _service;

    public FullCoverageTests(WebApplicationFactory<Program> factory)
    {
        _service = factory.Services.GetRequiredService<IWordMappingService>();
    }

    [Fact(Skip = "Extremely intensive test - iterates the entire UK grid")]
    public void WordPairs_AreUnique_ForAllUKCoordinates()
    {
        var hash = new HashSet<string>();
        var expectedCount = 0;

        for (int latIndex = 0; latIndex < _service.LatCount; latIndex++)
        {
            for (int lonIndex = 0; lonIndex < _service.LonCount; lonIndex++)
            {
                if (!_service.IsValidCoordinate(latIndex, lonIndex))
                    continue;

                var latWord = _service.GetWordAtIndex(latIndex);
                var lonWord = _service.GetWordAtIndex(lonIndex);
                var words = $"{latWord}.{lonWord}";

                expectedCount++;
                Assert.True(hash.Add(words), $"Clash found for {words} at [{latIndex},{lonIndex}]");
            }
        }

        Assert.Equal(expectedCount, hash.Count);
    }
}
