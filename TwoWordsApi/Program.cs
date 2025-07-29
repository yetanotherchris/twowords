using System.IO.Compression;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

// Load dictionaries. The expanded word list is stored as a zip archive at
// the repository root. To keep the repository size small we unzip it at
// startup and split the words between latitude and longitude lists.
var zipPath = Path.GetFullPath(Path.Combine(app.Environment.ContentRootPath,
    "..", "expanded_words.zip"));
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

if (allWords.Length < latCount + lonCount)
    throw new Exception("Word list is not large enough for coverage.");

var latWords = allWords.Take(latCount).ToArray();
var lonWords = allWords.Skip(latCount).Take(lonCount).ToArray();

app.MapGet("/words", (double lat, double lon) =>
{
    if (lat < latMin || lat > latMax || lon < lonMin || lon > lonMax)
    {
        return Results.BadRequest("Coordinates out of range");
    }

    var latIndex = (int)Math.Floor((lat - latMin) / step);
    var lonIndex = (int)Math.Floor((lon - lonMin) / step);

    if (latIndex >= latWords.Length || lonIndex >= lonWords.Length)
    {
        return Results.BadRequest("Word lists are too small for these coordinates");
    }

    var result = new
    {
        latitudeWord = latWords[latIndex],
        longitudeWord = lonWords[lonIndex]
    };

    return Results.Ok(result);
});

app.Run();

// Needed for integration tests
public partial class Program { }
