# TwoWords Data Pipeline Scripts

This folder contains PowerShell scripts to run the TwoWords data pipeline and prepare the word list for the API.

## Scripts

### `run-pipeline.ps1` (Docker Version)
Runs the complete data pipeline using Docker containers.

**Usage:**
```powershell
.\run-pipeline.ps1 [-Help]
```

**Parameters:**
- `-Help`: Show help message

**Requirements:**
- Docker Desktop installed and running
- Sufficient disk space for Docker images and data

**Steps performed:**
1. Builds the twowords-data Docker image
2. Runs all pipeline steps in order:
   - download-polygon (only if polygon file doesn't exist)
   - popular
   - filter
   - calculate-indices
   - optimize
   - verify
   - zip
3. Generates `words.zip` directly in the root folder

### `run-pipeline-local.ps1` (Local Python Version)
Runs the complete data pipeline using local Python installation.

**Usage:**
```powershell
.\run-pipeline-local.ps1 [-Help]
```

**Parameters:**
- `-Help`: Show help message

**Requirements:**
- Python 3.8+ installed and in PATH
- Python packages from `data/python/requirements.txt` (script will attempt to install them)

**Steps performed:**
1. Checks Python availability and installs requirements if needed
2. Runs all pipeline steps locally in order
3. Generates `words.zip` directly in the root folder

## Pipeline Steps (In Order)

The scripts run these steps in the correct sequence:

1. **download-polygon**: Downloads the UK/Ireland polygon data
2. **popular**: Generates the initial popular word list from multiple sources
3. **filter**: Filters words for the UK/Ireland polygon (marks out-of-bounds indices)
4. **calculate-indices**: Calculates indices for major UK cities
5. **optimize**: Optimizes word placement at population centers
6. **verify**: Verifies the mapping correctness
7. **zip**: Creates the final words.zip file

## Output

Both scripts will:
- Create/update files in the `data/output/` directory
- Generate `words.zip` directly in the root folder for the API to use
- Display progress and success/error messages

## API Integration

After running either script successfully, the API will automatically use the new `words.zip` file when it starts up. The `WordMappingService` looks for `words.zip` in the root folder (or `/words.zip` when running in a container).

## Troubleshooting

### Docker Version Issues
- Ensure Docker Desktop is running
- Check that you have sufficient disk space
- If the build fails, try: `docker system prune` to clean up

### Local Python Version Issues
- Ensure Python 3.8+ is installed and in PATH
- If package installation fails, try: `pip install --upgrade pip` first
- Run from the repository root directory

### General Issues
- Check that you're running the script from the twowords repository root
- Ensure you have write permissions to the repository folder
- Check network connectivity for downloading polygon data

## Data Attribution

The pipeline uses data from multiple sources including:
- Peter Norvig's word frequency list
- WordNet lexical database
- ChatGPT generated content
- UK/Ireland geographic boundaries

See `data/python/README.md` for full attribution details.
