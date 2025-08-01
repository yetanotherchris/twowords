#!/usr/bin/env pwsh
#
# TwoWords Data Pipeline Runner
# This script runs the Python data pipeline steps in the correct order using Docker
# and generates the words.zip file directly in the root folder for the API to use.
#

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "TwoWords Data Pipeline Runner" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run-pipeline.ps1 [-Help]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "This script will:"
    Write-Host "1. Build the twowords-data Docker image"
    Write-Host "2. Run all pipeline steps in the correct order:"
    Write-Host "   - download-polygon (only if polygon file doesn't exist)"
    Write-Host "   - popular"
    Write-Host "   - filter"
    Write-Host "   - calculate-indices"
    Write-Host "   - optimize"
    Write-Host "   - verify"
    Write-Host "   - zip"
    Write-Host "3. Generate words.zip file in the root folder"
    Write-Host ""
    exit 0
}

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        docker version *>$null
        return $true
    }
    catch {
        return $false
    }
}

# Function to run a pipeline step
function Invoke-PipelineStep {
    param(
        [string]$StepName,
        [string]$Command
    )
    
    Write-Host ""
    Write-Host "Running step: $StepName" -ForegroundColor Yellow
    Write-Host "Command: docker run --rm -v `"$(Get-Location)/data/output:/output`" twowords-data $Command" -ForegroundColor Gray
    
    $result = docker run --rm -v "$(Get-Location)/data/output:/output" twowords-data $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Step '$StepName' failed!" -ForegroundColor Red
        Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Step '$StepName' completed successfully" -ForegroundColor Green
    if ($result) {
        Write-Host $result
    }
}

# Main script execution
Write-Host "TwoWords Data Pipeline Runner" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Check if Docker is running
if (-not (Test-DockerRunning)) {
    Write-Host "ERROR: Docker is not running or not installed!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Create output directory if it doesn't exist
$outputDir = "data/output"
if (-not (Test-Path $outputDir)) {
    Write-Host "Creating output directory: $outputDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Build Docker image
Write-Host ""
Write-Host "Building Docker image: twowords-data" -ForegroundColor Yellow
docker build -f data/Dockerfile -t twowords-data .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Docker image!" -ForegroundColor Red
    exit 1
}
Write-Host "Docker image built successfully" -ForegroundColor Green

# Run pipeline steps in correct order
Write-Host ""
Write-Host "Starting data pipeline execution..." -ForegroundColor Green

# Step 1: Download polygon data (only if it doesn't exist)
$polygonFile = "data/polygons/uk_polygon.wkt.zip"
if (Test-Path $polygonFile) {
    Write-Host ""
    Write-Host "Polygon file already exists at $polygonFile - skipping download" -ForegroundColor Green
} else {
    Invoke-PipelineStep "Download Polygon" "download-polygon"
}

# Step 2: Generate popular word list
Invoke-PipelineStep "Generate Popular Words" "popular"

# Step 3: Filter words for polygon
Invoke-PipelineStep "Filter Words for Polygon" "filter"

# Step 4: Calculate indices for major cities
Invoke-PipelineStep "Calculate City Indices" "calculate-indices"

# Step 5: Optimize word placement
Invoke-PipelineStep "Optimize Word List" "optimize"

# Step 6: Verify mapping correctness
Invoke-PipelineStep "Verify Indices" "verify"

# Step 7: Generate final zip file
Invoke-PipelineStep "Generate ZIP File" "zip"

# Verify words.zip was created
Write-Host ""
Write-Host "Verifying words.zip was created..." -ForegroundColor Yellow

$targetZip = "words.zip"

if (Test-Path $targetZip) {
    Write-Host "Successfully created $targetZip" -ForegroundColor Green
} else {
    Write-Host "ERROR: File $targetZip not found!" -ForegroundColor Red
    Write-Host "The pipeline may have failed to generate the zip file." -ForegroundColor Red
    exit 1
}

# Verify the final file
if (Test-Path $targetZip) {
    $fileSize = (Get-Item $targetZip).Length
    Write-Host ""
    Write-Host "Pipeline completed successfully!" -ForegroundColor Green
    Write-Host "Final words.zip file size: $([math]::Round($fileSize / 1MB, 2)) MB" -ForegroundColor Green
    Write-Host "The API can now use the updated word list." -ForegroundColor Green
} else {
    Write-Host "ERROR: Final words.zip file was not created!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Data pipeline execution completed!" -ForegroundColor Green
Write-Host "You can now run the API with the updated word list." -ForegroundColor Cyan
