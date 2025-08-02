using Microsoft.AspNetCore.HttpOverrides;
using TwoWordsApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure forwarded headers for reverse proxy scenarios (like Fly.io)
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = Microsoft.AspNetCore.HttpOverrides.ForwardedHeaders.XForwardedFor | 
                              Microsoft.AspNetCore.HttpOverrides.ForwardedHeaders.XForwardedProto;
    // Trust any proxy (for cloud deployments)
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddOpenApi();

// Register GeoWordMapper as a singleton
builder.Services.AddSingleton<GeoWordMapper>(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IWebHostEnvironment>();

    string geoJsonPath = Path.Combine(environment.ContentRootPath, "central-uk.json");
    
    // Determine paths for words
    var isInContainer = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";
    string wordListPath;

    if (isInContainer)
    {
        wordListPath = "/words.zip";
    }
    else
    {
        wordListPath = Path.GetFullPath(Path.Combine(environment.ContentRootPath, "..", "..", "words.zip"));
    }

    // Create temporary word list file from zip for GeoWordMapper
    string tempWordListPath = Path.GetTempFileName();
    using (var zip = System.IO.Compression.ZipFile.OpenRead(wordListPath))
    {
        var wordsEntry = zip.Entries.FirstOrDefault(e => e.Name == "words.txt");
        if (wordsEntry == null)
        {
            throw new FileNotFoundException("words.txt not found in words.zip");
        }
        
        using (var stream = wordsEntry.Open())
        using (var reader = new StreamReader(stream))
        using (var writer = new StreamWriter(tempWordListPath))
        {
            string? line;
            while ((line = reader.ReadLine()) != null)
            {
                if (!string.IsNullOrWhiteSpace(line))
                    writer.WriteLine(line.Trim());
            }
        }
    }

    return new GeoWordMapper(geoJsonPath, tempWordListPath);
});

// Register the word mapping service as a singleton
builder.Services.AddSingleton<IWordMappingService, WordMappingService>();

var app = builder.Build();

// Configure forwarded headers middleware (must be early in pipeline)
app.UseForwardedHeaders();

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

// Map controllers
app.MapControllers();

// Redirect root to Swagger UI
app.MapGet("/", () => Results.Redirect("/swagger"))
.ExcludeFromDescription();

app.Run();

// Needed for integration tests
public partial class Program { }
