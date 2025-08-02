using Microsoft.AspNetCore.Mvc;
using TwoWordsApi.Services;

namespace TwoWordsApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class MapController : ControllerBase
{
    private readonly IWordMappingService _wordMappingService;

    public MapController(IWordMappingService wordMappingService)
    {
        _wordMappingService = wordMappingService;
    }

    [HttpGet("/map")]
    [ProducesResponseType(typeof(string), 200)]
    [ProducesResponseType(400)]
    public IActionResult GetMapView(
        [FromQuery] string words, 
        [FromQuery] int? zoom = 15)
    {
        // Parse the input format "word1.word2"
        var wordParts = words.Split('.');
        if (wordParts.Length != 2)
        {
            return BadRequest("Words must be in format 'word1.word2'");
        }

        var latitudeWord = wordParts[0].Trim();
        var longitudeWord = wordParts[1].Trim();

        // Find the indices of the words in the array
        var latIndex = _wordMappingService.FindWordIndex(latitudeWord);
        var lonIndex = _wordMappingService.FindWordIndex(longitudeWord);

        if (latIndex == -1)
        {
            return BadRequest($"Latitude word '{wordParts[0]}' not found in word list");
        }

        if (lonIndex == -1)
        {
            return BadRequest($"Longitude word '{wordParts[1]}' not found in word list");
        }

        // Get coordinates using the new method
        var coordinates = _wordMappingService.GetCoordinatesFromWords(latitudeWord, longitudeWord);
        
        if (coordinates == null)
        {
            return BadRequest("Unable to determine coordinates for these words");
        }

        var (lat, lon) = coordinates.Value;

        // Validate that the coordinates are valid
        if (!_wordMappingService.IsValidCoordinate(lat, lon))
        {
            return BadRequest("The coordinates for these words are outside the loaded polygon");
        }

        // Clamp zoom level between 1 and 19
        var clampedZoom = Math.Max(1, Math.Min(19, zoom ?? 15));

        // Calculate grid bounds for visualization (use a small fixed grid size)
        var gridSize = 0.0001; // ~10m at UK latitudes
        var gridEndLat = lat + gridSize;
        var gridEndLon = lon + gridSize;

        // Get polygon statistics for display
        var polygonStats = _wordMappingService.GetPolygonStatistics();

        // Get polygon coordinates for visualization
        var polygons = _wordMappingService.GetPolygonCoordinates();
        
        // Convert polygon coordinates to JavaScript format
        var polygonJs = string.Join(",", polygons.Select(polygon => 
            "[" + string.Join(",", polygon.Select(point => $"[{point.Latitude:F6}, {point.Longitude:F6}]")) + "]"
        ));

        // Create HTML page with embedded map
        var html = $@"<!DOCTYPE html>
<html lang=""en"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>TwoWords Map: {words}</title>
    <link rel=""stylesheet"" href=""https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"" />
    <script src=""https://unpkg.com/leaflet@1.9.4/dist/leaflet.js""></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: #3b82f6;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .info {{
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            background: #f8fafc;
        }}
        .coordinate-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .info-item {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #3b82f6;
        }}
        .info-item strong {{
            color: #1f2937;
        }}
        .map-container {{
            padding: 20px;
            text-align: center;
        }}
        #map {{
            height: 450px;
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .map-container iframe {{
            border: 1px solid #d1d5db;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .controls {{
            padding: 15px 20px;
            background: #f8fafc;
            border-top: 1px solid #e5e7eb;
            text-align: center;
        }}
        .btn {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            margin: 0 5px;
            display: inline-block;
            cursor: pointer;
        }}
        .btn:hover {{
            background: #2563eb;
        }}
        .precision-note {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .map-link {{
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .map-link a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        .map-link a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class=""container"">
        <div class=""header"">
            <h1>📍 {words}</h1>
            <p>TwoWords Location Map</p>
        </div>
        
        <div class=""info"">
            <div class=""coordinate-info"">
                <div class=""info-item"">
                    <strong>Words:</strong> {wordParts[0]} . {wordParts[1]}
                </div>
                <div class=""info-item"">
                    <strong>Coordinates:</strong> {lat:F4}°N, {Math.Abs(lon):F4}°{(lon < 0 ? "W" : "E")}
                </div>
                <div class=""info-item"">
                    <strong>Precision:</strong> ~10 meter grid
                </div>
                <div class=""info-item"">
                    <strong>Indices:</strong> lat[{latIndex}], lon[{lonIndex}]
                </div>
                <div class=""info-item"">
                    <strong>Coverage:</strong> {polygons.Count} polygon(s)
                </div>
            </div>
            <div class=""precision-note"">
                <strong>Note:</strong> This location represents a ~10×10 meter grid square. The exact coordinates shown are the southwestern corner of that grid.
            </div>
        </div>

        <div class=""map-container"">
            <div id=""map""></div>
            <div class=""map-link"">
                <a href=""https://www.openstreetmap.org/?mlat={lat:F6}&amp;mlon={lon:F6}#map={clampedZoom}/{lat:F6}/{lon:F6}"" target=""_blank"">
                    View Larger Map
                </a>
            </div>
        </div>
        
        <div class=""controls"">
            <a href=""https://www.openstreetmap.org/search?query={lat:F6}%2C+{lon:F6}"" target=""_blank"" class=""btn"">
                🗺️ Open in OpenStreetMap
            </a>
            <a href=""https://www.google.com/maps?q={lat:F6},{lon:F6}"" target=""_blank"" class=""btn"">
                🌍 Open in Google Maps
            </a>
            <button onclick=""copyCoordinates()"" class=""btn"">
                📋 Copy Coordinates
            </button>
        </div>
    </div>

    <script>
        // Initialize map
        var map = L.map('map').setView([{lat:F6}, {lon:F6}], {clampedZoom});

        // Add OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href=""https://www.openstreetmap.org/copyright"">OpenStreetMap</a> contributors'
        }}).addTo(map);

        // Add polygon(s) to map
        var polygonCoords = [{polygonJs}];
        polygonCoords.forEach(function(coords) {{
            L.polygon(coords, {{
                color: '#3b82f6',
                weight: 2,
                opacity: 0.8,
                fillColor: '#3b82f6',
                fillOpacity: 0.1
            }}).addTo(map);
        }});

        // Add marker for the specific location
        var marker = L.marker([{lat:F6}, {lon:F6}]).addTo(map);
        marker.bindPopup('<b>{words}</b><br>Lat: {lat:F4}°N<br>Lon: {Math.Abs(lon):F4}°{(lon < 0 ? "W" : "E")}');

        // Add grid square visualization
        var gridSquare = L.rectangle([
            [{lat:F6}, {lon:F6}],
            [{lat + gridSize:F6}, {lon + gridSize:F6}]
        ], {{
            color: '#f59e0b',
            weight: 2,
            opacity: 0.8,
            fillColor: '#f59e0b',
            fillOpacity: 0.3
        }}).addTo(map);
        gridSquare.bindPopup('Grid Square (~10m × 10m)');

        // Copy coordinates function
        function copyCoordinates() {{
            const coords = '{lat:F6}, {lon:F6}';
            navigator.clipboard.writeText(coords).then(() => {{
                alert('Coordinates copied to clipboard: ' + coords);
            }}).catch(() => {{
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = coords;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Coordinates copied to clipboard: ' + coords);
            }});
        }}
    </script>
</body>
</html>";

        return Content(html, "text/html");
    }
}
