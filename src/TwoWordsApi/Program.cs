using System.IO.Compression;
using System.Text;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
// Enable OpenAPI and Swagger in all environments for public API
app.MapOpenApi();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/openapi/v1.json", "TwoWords API v1");
    options.DocumentTitle = "TwoWords API Documentation";
    options.HeadContent = @"
        <style>
            .swagger-ui .topbar { display: none; }
            .swagger-ui .info .title { color: #3b82f6; }
        </style>";
});


// Determine the correct path for expanded_words.zip
// In container: /expanded_words.zip (copied to root)
// Local development: ../../expanded_words.zip (relative to ContentRootPath)
string zipPath;
var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";

if (isInContainer)
{
    zipPath = "/expanded_words.zip";
}
else
{
    zipPath = Path.GetFullPath(Path.Combine(app.Environment.ContentRootPath,
        "..", "..", "expanded_words.zip"));
}

// Verify the file exists
if (!File.Exists(zipPath))
{
    throw new FileNotFoundException($"expanded_words.zip not found at {zipPath}. " +
        $"ContentRootPath: {app.Environment.ContentRootPath}, " +
        $"IsInContainer: {isInContainer}");
}

string[] allWords;
using (var zip = ZipFile.OpenRead(zipPath))
using (var stream = zip.Entries.First().Open())
using (var reader = new StreamReader(stream))
{
    var words = new List<string>();
    string? line;
    while ((line = reader.ReadLine()) != null)
    {
        if (!string.IsNullOrWhiteSpace(line))
            words.Add(line.Trim());
    }
    allWords = words.ToArray();
}

const double latMin = 49.0;
const double latMax = 60.0;
const double lonMin = -8.0;
const double lonMax = 2.0;
const double step = 0.0001; // ~10m

int latCount = (int)Math.Ceiling((latMax - latMin) / step) + 1;
int lonCount = (int)Math.Ceiling((lonMax - lonMin) / step) + 1;

// We use the same dictionary for both latitude and longitude indices. Ensure
// it is large enough to cover the larger of the two ranges.
if (allWords.Length < Math.Max(latCount, lonCount))
    throw new Exception("Word list is not large enough for coverage.");

// Simple land validation rules for UK/Ireland
static bool IsLikelyLand(double lat, double lon)
{
    // Rule 1: Exclude major seas around UK/Ireland
    // Irish Sea (rough boundaries)
    if (lat >= 53.0 && lat <= 55.5 && lon >= -6.0 && lon <= -3.0) return false;
    
    // North Sea (eastern edge)
    if (lon > 1.0) return false;
    
    // Atlantic Ocean (western edge)
    if (lon < -7.0) return false;
    
    // English Channel (southern edge)
    if (lat < 50.0) return false;
    
    // Rule 2: Exclude Scottish Highlands (very mountainous/remote)
    if (lat > 57.0 && lon >= -5.0 && lon <= -2.0) return false;
    
    // Rule 3: Exclude major lochs/lakes
    // Loch Ness area
    if (lat >= 57.2 && lat <= 57.4 && lon >= -4.7 && lon <= -4.4) return false;
    
    // Rule 4: Exclude Shetland/Orkney (too remote)
    if (lat > 58.5) return false;
    
    // Rule 5: Exclude Isle of Man (in Irish Sea)
    if (lat >= 54.0 && lat <= 54.5 && lon >= -4.8 && lon <= -4.3) return false;
    
    // Rule 6: Exclude Anglesey (Welsh island)
    if (lat >= 53.1 && lat <= 53.4 && lon >= -4.8 && lon <= -4.2) return false;
    
    // Rule 7: Exclude Northern Ireland mountainous areas
    if (lat >= 54.5 && lat <= 55.3 && lon >= -7.0 && lon <= -5.5) return false;
    
    // Rule 8: Exclude Dartmoor/Exmoor (Southwest England highlands)
    if (lat >= 50.4 && lat <= 51.3 && lon >= -4.2 && lon <= -3.3) return false;
    
    // Rule 9: Exclude Lake District (Cumbrian mountains)
    if (lat >= 54.3 && lat <= 54.8 && lon >= -3.4 && lon <= -2.9) return false;
    
    // Rule 10: Exclude Snowdonia (Welsh mountains)
    if (lat >= 52.7 && lat <= 53.2 && lon >= -4.1 && lon <= -3.6) return false;
    
    return true;
}

app.MapGet("/stats", () =>
{
    var stats = $"Total words: {allWords.Length}\n" +
                $"Latitude range: {latMin} to {latMax}\n" +
                $"Longitude range: {lonMin} to {lonMax}\n" +
                $"Step (precision): {step}\n";

    return Results.Text(stats);
})
.WithName("GetStats")
.WithSummary("Get system statistics")
.WithDescription("Returns statistics about the TwoWords system including word count, coordinate ranges, and precision")
.WithTags("System")
.Produces<string>(200, "text/plain");

app.MapGet("/words", (double lat, double lon) =>
{
    if (lat < latMin || lat > latMax || lon < lonMin || lon > lonMax)
    {
        return Results.BadRequest("Coordinates out of range");
    }

    if (!IsLikelyLand(lat, lon))
    {
        return Results.BadRequest("Coordinates appear to be over water or inaccessible terrain");
    }

    var latIndex = (int)Math.Floor((lat - latMin) / step);
    var lonIndex = (int)Math.Floor((lon - lonMin) / step);

    if (latIndex >= latCount || lonIndex >= lonCount)
    {
        return Results.BadRequest("Word list is too small for these coordinates");
    }

    var result = new
    {
        latitudeWord = allWords[latIndex],
        longitudeWord = allWords[lonIndex]
    };

    return Results.Text($"{result.latitudeWord}.{result.longitudeWord}");
})
.WithName("GetWords")
.WithSummary("Convert coordinates to two words")
.WithDescription("Maps latitude/longitude coordinates to a unique two-word combination. Only covers UK/Ireland land areas (49.0°-60.0°N, -8.0°-2.0°E) with ~10m precision.")
.WithTags("Mapping")
.Produces<string>(200, "text/plain")
.Produces(400)
.WithOpenApi(operation => new(operation)
{
    Parameters = [
        new() { Name = "lat", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = true, Description = "Latitude coordinate (49.0 to 60.0)", Schema = new() { Type = "number", Format = "double", Minimum = 49.0m, Maximum = 60.0m } },
        new() { Name = "lon", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = true, Description = "Longitude coordinate (-8.0 to 2.0)", Schema = new() { Type = "number", Format = "double", Minimum = -8.0m, Maximum = 2.0m } }
    ]
});

app.MapGet("/validate", (double lat, double lon) =>
{
    if (lat < latMin || lat > latMax || lon < lonMin || lon > lonMax)
    {
        return Results.Ok(new { isValid = false, reason = "Out of range" });
    }

    var isLand = IsLikelyLand(lat, lon);
    return Results.Ok(new { 
        isValid = isLand, 
        reason = isLand ? "Valid land coordinates" : "Water or inaccessible terrain" 
    });
})
.WithName("ValidateCoordinates")
.WithSummary("Validate if coordinates are mappable")
.WithDescription("Checks if the given coordinates are within the supported range and over land (not water or inaccessible terrain)")
.WithTags("Validation")
.Produces<object>(200)
.WithOpenApi(operation => new(operation)
{
    Parameters = [
        new() { Name = "lat", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = true, Description = "Latitude coordinate (49.0 to 60.0)", Schema = new() { Type = "number", Format = "double", Minimum = 49.0m, Maximum = 60.0m } },
        new() { Name = "lon", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = true, Description = "Longitude coordinate (-8.0 to 2.0)", Schema = new() { Type = "number", Format = "double", Minimum = -8.0m, Maximum = 2.0m } }
    ]
});

app.MapGet("/coordinates", (string words, string? format = "lat,lon") =>
{
    // Parse the input format "word1.word2"
    var wordParts = words.Split('.');
    if (wordParts.Length != 2)
    {
        return Results.BadRequest("Words must be in format 'word1.word2'");
    }

    var latitudeWord = wordParts[0].Trim().ToLower();
    var longitudeWord = wordParts[1].Trim().ToLower();

    // Find the indices of the words in the array
    var latIndex = Array.FindIndex(allWords, w => w.ToLower() == latitudeWord);
    var lonIndex = Array.FindIndex(allWords, w => w.ToLower() == longitudeWord);

    if (latIndex == -1)
    {
        return Results.BadRequest($"Latitude word '{wordParts[0]}' not found in word list");
    }

    if (lonIndex == -1)
    {
        return Results.BadRequest($"Longitude word '{wordParts[1]}' not found in word list");
    }

    // Check if indices are within valid coordinate range
    if (latIndex >= latCount)
    {
        return Results.BadRequest($"Latitude word '{wordParts[0]}' corresponds to coordinates outside the supported range");
    }

    if (lonIndex >= lonCount)
    {
        return Results.BadRequest($"Longitude word '{wordParts[1]}' corresponds to coordinates outside the supported range");
    }

    // Convert indices back to coordinates
    var lat = latMin + (latIndex * step);
    var lon = lonMin + (lonIndex * step);

    // Validate that the coordinates are likely land
    if (!IsLikelyLand(lat, lon))
    {
        return Results.BadRequest("The coordinates for these words appear to be over water or inaccessible terrain");
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

    return Results.Text(response);
})
.WithName("GetCoordinates")
.WithSummary("Convert two words back to coordinates")
.WithDescription("Converts a two-word combination back to the original latitude/longitude coordinates. Words must be in 'word1.word2' format.")
.WithTags("Mapping")
.Produces<string>(200, "text/plain")
.Produces(400)
.WithOpenApi(operation => new(operation)
{
    Parameters = [
        new() { Name = "words", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = true, Description = "Two words in format 'word1.word2' (e.g., 'apple.banana')", Schema = new() { Type = "string", Pattern = @"^[a-zA-Z]+\.[a-zA-Z]+$" } },
        new() { Name = "format", In = Microsoft.OpenApi.Models.ParameterLocation.Query, Required = false, Description = "Output format: 'lat,lon' (default) or 'lon,lat'", Schema = new() { Type = "string" } }
    ]
});

app.MapGet("/examples", () =>
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
        if (city.Lat >= latMin && city.Lat <= latMax && city.Lon >= lonMin && city.Lon <= lonMax)
        {
            var latIndex = (int)Math.Floor((city.Lat - latMin) / step);
            var lonIndex = (int)Math.Floor((city.Lon - lonMin) / step);

            if (latIndex < latCount && lonIndex < lonCount)
            {
                examples.Add($"{city.Name} - {allWords[latIndex]}.{allWords[lonIndex]} ({city.Lon}, {city.Lat})");
            }
        }
    }

    // Process landmarks
    foreach (var landmark in landmarks)
    {
        if (landmark.Lat >= latMin && landmark.Lat <= latMax && landmark.Lon >= lonMin && landmark.Lon <= lonMax)
        {
            var latIndex = (int)Math.Floor((landmark.Lat - latMin) / step);
            var lonIndex = (int)Math.Floor((landmark.Lon - lonMin) / step);

            if (latIndex < latCount && lonIndex < lonCount)
            {
                examples.Add($"{landmark.Name} - {allWords[latIndex]} {allWords[lonIndex]} ({landmark.Lon}, {landmark.Lat})");
            }
        }
    }

    return Results.Ok(examples);
})
.WithName("GetExamples")
.WithSummary("Get example word mappings")
.WithDescription("Returns example two-word mappings for famous UK cities and landmarks to demonstrate the system")
.WithTags("Examples")
.Produces<List<string>>(200);

// Redirect root to Swagger UI
app.MapGet("/", () => Results.Redirect("/swagger"))
.ExcludeFromDescription();

app.Run();

// Needed for integration tests
public partial class Program { }
