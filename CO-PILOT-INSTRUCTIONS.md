# Co-Pilot Instructions for TwoWords Project

This document provides detailed instructions for using GitHub Copilot and other AI assistants to work effectively on both the Python (data pipeline) and C# (.NET API) parts of the TwoWords project.

---

## General Guidelines
- Always attribute data sources and code origins in documentation and comments.
- Ensure all scripts and services are stateless and reproducible.
- Prioritize code clarity, modularity, and testability.
- Use the CLI for all data pipeline operations; do not edit output files manually.
- Validate all changes with unit tests or CLI checks where possible.

---

## Python (Data Pipeline)

### Key Files
- `twowords_cli.py`: Main entry point for all operations.
- `words_create_inital_curated_list.py`: Generates the initial word list from multiple sources.
- `words_filter_for_polygon.py`: Filters words by UK/Ireland polygon.
- `optimize_word_list.py`: Scores and optimizes the word list.
- `calculate_popular_indices.py`: Calculates indices for major cities.
- `verify_indices.py`: Validates mapping correctness.
- `twowords_utils/`: Utility modules for word curation, polygon handling, and zip management.

### How to Use
1. Run `python twowords_cli.py --help` to see available commands.
2. Use the CLI to execute each pipeline step in order:
   - Generate initial list
   - Filter for polygon
   - Optimize word list
   - Calculate popular indices
   - Verify indices
3. All outputs are written to the `data/output/` directory.
4. Do not edit output files by hand; always use the pipeline.

### Best Practices
- Document any new data sources or scripts.
- Keep utility functions in `twowords_utils/` for reuse.
- Attribute all data sources, including ChatGPT and Norvig.
- Ensure scripts are idempotent and can be rerun safely.

---

## C# (.NET API)

### Key Files
- `Controllers/TwoWordsController.cs`: Main API controller for word lookup.
- `Controllers/MapController.cs`: Map and polygon endpoints.
- `Services/WordMappingService.cs`: Core mapping logic.
- `Services/IWordMappingService.cs`: Mapping service interface.
- `Program.cs`: API entry point and configuration.

### How to Use
1. Build the solution using `dotnet build`.
2. Run the API with `dotnet run --project src/TwoWordsApi/TwoWordsApi.csproj`.
3. Use the `/api/words` endpoint to look up word pairs by coordinates or index.
4. Use the `/api/map` endpoints for polygon and mapping queries.
5. Update the word list by replacing `data/output/words.txt` with a new pipeline output.

### Best Practices
- Keep mapping logic deterministic and stateless.
- Add unit tests for all new endpoints and services.
- Document API changes in `README.md` and code comments.
- Attribute all data and code sources.

---

## Attribution
- Always credit Peter Norvig, WordNet, ChatGPT, and any other data or code sources in documentation and comments.
- See `data/python/README.md` for full data pipeline attribution.

---

For questions or improvements, see the main project `README.md` or contact the maintainers.
