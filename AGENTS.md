# Repository Contributor Guidelines

## Code Formatting
- Stick to the existing style in the project when editing C# or Python files.

## Testing
- Run all tests before submitting a pull request:
  ```bash
  dotnet test tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj -c Release
  ```
  Ensure the test suite completes without failures.

## Large Files
- **Do not add large zip archives or text files to the repository.**
  - Avoid committing new `.zip` or `.txt` files larger than **1&nbsp;MB**.
  - If large data is required, host it externally and download it during tests or use a smaller sample.
  - The file `python/word-data/uk_polygon.wkt.zip` should not be committed; download it when needed using the provided script.

## Pull Requests
- Keep PRs focused and limit them to necessary changes.
- Provide clear descriptions of the changes and reference any related issues.
