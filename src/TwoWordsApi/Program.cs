using System.Text.Json.Nodes;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.OpenApi;
using Scalar.AspNetCore;
using TwoWordsApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure forwarded headers for reverse proxy scenarios (like Fly.io)
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = Microsoft.AspNetCore.HttpOverrides.ForwardedHeaders.XForwardedFor | 
                              Microsoft.AspNetCore.HttpOverrides.ForwardedHeaders.XForwardedProto;
    // Trust any proxy (for cloud deployments)
    options.KnownIPNetworks.Clear();
    options.KnownProxies.Clear();
});

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddOpenApi(options =>
{
    // Set the introduction shown at the top of the Scalar docs (rendered as markdown)
    options.AddDocumentTransformer((document, _, _) =>
    {
        document.Info.Title = "TwoWords API";
        document.Info.Version = "v1";
        document.Info.Description = """
            **TwoWords** turns a UK location into two memorable words — and back again.
            Every ~10×10 m grid square inside the covered area maps to a unique `word1.word2` pair.

            ## How to use it

            **Coordinates → words** — find the two words for a latitude/longitude:
            ```
            GET /words?lat=51.2719&lon=0.1904   →   estrade.rainout
            ```

            **Words → coordinates** — resolve a word pair back to a location:
            ```
            GET /coordinates?words=estrade.rainout   →   51.2719, 0.1904
            ```

            **Words → map** — open an interactive Leaflet map for a word pair:
            ```
            GET /map?words=estrade.rainout
            ```

            ## Other endpoints

            - `GET /validate?lat={lat}&lon={lon}` — check whether coordinates fall inside the covered area.
            - `GET /stats` — word list size, precision, and polygon bounds.
            - `GET /examples` — sample word pairs for well-known UK cities and landmarks.

            ## Notes

            - Coverage is limited to a central-UK polygon (roughly lat 50.24–56.33, lon -4.72–1.72). Coordinates outside it return `400`.
            - Words use the `word1.word2` format, where the first word encodes latitude and the second longitude.
            - Precision is ~11 m; the returned coordinate is the south-west corner of the grid square.
            """;

        return Task.CompletedTask;
    });

    // Prefill the /map "words" example with a real location (Sevenoaks, Kent: estrade.rainout)
    options.AddOperationTransformer((operation, context, _) =>
    {
        if (context.Description.RelativePath == "map" && operation.Parameters is not null)
        {
            if (operation.Parameters.FirstOrDefault(p => p.Name == "words") is OpenApiParameter wordsParam)
            {
                wordsParam.Example = JsonValue.Create("estrade.rainout");
            }
        }

        return Task.CompletedTask;
    });
});

// Register GeoWordMapper as a singleton
builder.Services.AddSingleton<GeoWordMapper>(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IWebHostEnvironment>();

    string geoJsonPath = Path.Combine(environment.ContentRootPath, "central-uk.json");
    
    // Determine path for words.txt
    var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";
    string wordListPath;

    if (isInContainer)
    {
        wordListPath = "/app/words.txt";
    }
    else
    {
        wordListPath = Path.Combine(environment.ContentRootPath, "words.txt");
    }

    // Verify the words.txt file exists
    if (!File.Exists(wordListPath))
    {
        throw new FileNotFoundException($"words.txt not found at {wordListPath}");
    }

    return new GeoWordMapper(geoJsonPath, wordListPath);
});

// Register the word mapping service as a singleton
builder.Services.AddSingleton<IWordMappingService, WordMappingService>();

var app = builder.Build();

// Configure forwarded headers middleware (must be early in pipeline)
app.UseForwardedHeaders();

// Configure the HTTP request pipeline.
// Enable OpenAPI and the Scalar API reference UI in all environments for public API
app.MapOpenApi();
app.MapScalarApiReference(options =>
{
    options.Title = "TwoWords API";
});

// Map controllers
app.MapControllers();

// Redirect root to the Scalar API reference UI
app.MapGet("/", () => Results.Redirect("/scalar/v1"))
.ExcludeFromDescription();

app.Run();

// Needed for integration tests
public partial class Program { }
