var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

// Load dictionaries. In a real application these lists should contain
// enough words to cover every possible coordinate step.
var latWords = File.ReadAllLines(Path.Combine("data", "lat_words.txt"));
var lonWords = File.ReadAllLines(Path.Combine("data", "lon_words.txt"));

const double latMin = 49.0;
const double latMax = 60.0;
const double lonMin = -8.0;
const double lonMax = 2.0;
const double step = 0.0001; // ~10m

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
