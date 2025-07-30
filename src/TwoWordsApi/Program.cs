using System.IO.Compression;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/openapi/v1.json", "TwoWords API v1");
    });
}


var zipPath = Path.GetFullPath(Path.Combine(app.Environment.ContentRootPath,
    "..", "..", "expanded_words.zip"));

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

app.MapGet("/stats", () =>
{
    var stats = $"Total words: {allWords.Length}\n" +
                $"Latitude range: {latMin} to {latMax}\n" +
                $"Longitude range: {lonMin} to {lonMax}\n" +
                $"Step (precision): {step}\n";

    return Results.Text(stats);
});

app.MapGet("/words", (double lat, double lon) =>
{
    if (lat < latMin || lat > latMax || lon < lonMin || lon > lonMax)
    {
        return Results.BadRequest("Coordinates out of range");
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

    return Results.Ok(result);
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
                examples.Add($"{city.Name} - {allWords[latIndex]} {allWords[lonIndex]} ({city.Lon}, {city.Lat})");
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
});

// Redirect root to Swagger UI
app.MapGet("/", () => Results.Redirect("/swagger"))
.ExcludeFromDescription();

app.Run();

// Needed for integration tests
public partial class Program { }
