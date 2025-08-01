#!/usr/bin/env pwsh
#
# TwoWords Data Pipeline Runner (Local Python Version)
# This script runs the Python data pipeline steps locally without Docker
# and then copies the generated words.zip file to the root folder for the API to use.
#

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "TwoWords Data Pipeline Runner (Local Python)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run-pipeline-local.ps1 [-Help]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "This script will:"
    Write-Host "1. Check if Python and required packages are available"
    Write-Host "2. Run all pipeline steps in the correct order locally"
    Write-Host "3. Copy the generated words.zip file to the root folder"
    Write-Host ""
    Write-Host "Requirements:"
    Write-Host "- Python 3.8+ installed and in PATH"
    Write-Host "- Required Python packages (install with: pip install -r data/python/requirements.txt)"
    Write-Host ""
    exit 0
}

# Function to check if Python is available
function Test-PythonAvailable {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

# Function to run a pipeline step locally
function Invoke-LocalPipelineStep {
    param(
        [string]$StepName,
        [string]$Command
    )
    
    Write-Host ""
    Write-Host "Running step: $StepName" -ForegroundColor Yellow
    Write-Host "Command: python twowords_cli.py $Command" -ForegroundColor Gray
    
    Push-Location "data/python"
    try {
        $result = python twowords_cli.py $Command
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Step '$StepName' failed!" -ForegroundColor Red
            Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        Write-Host "Step '$StepName' completed successfully" -ForegroundColor Green
        if ($result) {
            Write-Host $result
        }
    }
    finally {
        Pop-Location
    }
}

# Main script execution
Write-Host "TwoWords Data Pipeline Runner (Local Python)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if Python is available
if (-not (Test-PythonAvailable)) {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again." -ForegroundColor Red
    Write-Host "You can download Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "data/python/twowords_cli.py")) {
    Write-Host "ERROR: Please run this script from the root of the twowords repository!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check if requirements are installed
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
Push-Location "data/python"
try {
    python -c "import shapely, requests, zipfile" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Some required Python packages are missing." -ForegroundColor Yellow
        Write-Host "Installing requirements..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to install Python requirements!" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    }
    Write-Host "Python dependencies are available" -ForegroundColor Green
}
finally {
    Pop-Location
}

# Create output directory if it doesn't exist
$outputDir = "data/output"
if (-not (Test-Path $outputDir)) {
    Write-Host "Creating output directory: $outputDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Run pipeline steps in correct order
Write-Host ""
Write-Host "Starting data pipeline execution..." -ForegroundColor Green

# Step 1: Download polygon data
Invoke-LocalPipelineStep "Download Polygon" "download-polygon"

# Step 2: Generate popular word list
Invoke-LocalPipelineStep "Generate Popular Words" "popular"

# Step 3: Filter words for polygon
Invoke-LocalPipelineStep "Filter Words for Polygon" "filter"

# Step 4: Calculate indices for major cities
Invoke-LocalPipelineStep "Calculate City Indices" "calculate-indices"

# Step 5: Optimize word placement
Invoke-LocalPipelineStep "Optimize Word List" "optimize"

# Step 6: Verify mapping correctness
Invoke-LocalPipelineStep "Verify Indices" "verify"

# Step 7: Generate final zip file
Invoke-LocalPipelineStep "Generate ZIP File" "zip"

# Copy words.zip to root folder
Write-Host ""
Write-Host "Copying words.zip to root folder..." -ForegroundColor Yellow

$sourceZip = "expanded_words.zip"
$targetZip = "words.zip"

if (Test-Path $sourceZip) {
    Copy-Item $sourceZip $targetZip -Force
    Write-Host "Successfully copied $sourceZip to $targetZip" -ForegroundColor Green
} else {
    Write-Host "ERROR: Source file $sourceZip not found!" -ForegroundColor Red
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
