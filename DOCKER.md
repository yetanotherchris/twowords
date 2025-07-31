# Docker Deployment Guide

This guide covers how to build and run the TwoWords API using Docker.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and run the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The API will be available at http://localhost:8080

### Using Docker directly

```bash
# Build the image
docker build -t twowords-api .

# Run the container
docker run -d -p 8080:8080 --name twowords-api twowords-api

# View logs
docker logs twowords-api

# Stop and remove the container
docker rm -f twowords-api
```

## Testing the Deployment

Once the container is running, you can test it:

```bash
# Check API stats
curl http://localhost:8080/stats

# Test word mapping for London
curl "http://localhost:8080/words?lat=51.5074&lon=-0.1278"

# View examples
curl http://localhost:8080/examples

# Access Swagger UI
# Open http://localhost:8080 in your browser
```

## Environment Variables

The container supports these environment variables:

- `ASPNETCORE_ENVIRONMENT`: Set to `Development` or `Production` (default: `Production`)
- `ASPNETCORE_URLS`: URLs the app listens on (default: `http://+:8080`)

## Health Check

The container includes a health check that calls the `/stats` endpoint every 30 seconds.

## File Structure

The Docker image includes:
- The compiled .NET application in `/app`
- The `geo_validated_words.zip` file at `/geo_validated_words.zip`
- All necessary .NET runtime dependencies

## Troubleshooting

### Container won't start
- Check logs: `docker logs <container-name>`
- Ensure port 8080 is not already in use
- Verify the `geo_validated_words.zip` file exists in the repository root

### API returns errors
- Ensure the zip file was copied correctly: `docker exec <container-name> ls -la /geo_validated_words.zip`
- Check that coordinates are within the UK/Ireland bounds (49.0°-60.0°N, -8.0°-2.0°E)

### Performance issues
- The word list is loaded into memory at startup, so initial load may take a moment
- Consider resource limits if running in a constrained environment
