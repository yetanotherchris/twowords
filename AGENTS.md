
# Repository Contributor Guidelines

## Code Formatting
- Stick to the existing style in the project when editing C# or Python files.

## Testing
- Run all tests before submitting a pull request:
  ```bash
  dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
  ```
  Ensure the test suite completes without failures.

## Data Directory Structure
- All word lists, polygons, and output files are now stored under the `data/` directory:
  - `data/words/` — All word list files (e.g., `norvig-word-list.txt`, `food_dishes_final.txt`, `important_indices.txt`, etc.)
  - `data/polygons/` — Polygon data (e.g., `uk_polygon.wkt.zip`)
  - `data/output/` — Generated output files (e.g., `words.txt`)

## Large Files
- **Do not add large zip archives or text files to the repository.**
  - Avoid committing new `.zip` or `.txt` files larger than 100 kilobytes. This will break Codex's PR requests.
  - If large data is required, host it externally and download it during tests or use a smaller sample.

## Pull Requests
- Keep PRs focused and limit them to necessary changes.
- Provide clear descriptions of the changes and reference any related issues.
