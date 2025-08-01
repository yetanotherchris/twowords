# Agents Overview

This document describes the agents, automation, and co-pilot instructions for both the Python and C# (.NET) parts of the TwoWords project.

---

## Python Agents (Data Pipeline)

### Purpose
Automate the generation, curation, filtering, and optimization of word lists for the TwoWords API, ensuring high quality and geographic relevance.

### Main Scripts & Agents
- **twowords_cli.py**: Main CLI entry point for all pipeline operations.
- **words_create_inital_curated_list.py**: Agent for merging and curating word sources (Norvig, WordNet, food dishes, ChatGPT, etc.).
- **words_filter_for_polygon.py**: Agent for filtering words by UK/Ireland polygon using geospatial logic.
- **optimize_word_list.py**: Agent for scoring and optimizing the word list for memorability and population centers.
- **calculate_popular_indices.py**: Agent for identifying grid indices for major cities.
- **twowords_utils/**: Utility agents for polygon handling, word curation, and zip management.

### Data Flow
1. **Input**: Multiple word sources (curated lists, WordNet, ChatGPT, frequency data).
2. **Processing**: Merge, deduplicate, filter, and score words.
3. **Geographic Filtering**: Remove words mapping to non-UK/Ireland land areas.
4. **Optimization**: Assign best words to population centers.
5. **Output**: Final word list for API use.

### Automation
- All scripts are stateless and reproducible.
- Designed for batch or scheduled runs.
- CLI supports modular execution of each step.

---

## C# Agents (API Backend)

### Purpose
Serve the TwoWords API, mapping coordinates to memorable word pairs and exposing endpoints for lookup and validation.

### Main Components & Agents
- **Controllers/TwoWordsController.cs**: Main API agent for word lookup and mapping endpoints.
- **Controllers/MapController.cs**: Agent for map-related endpoints and polygon queries.
- **Services/WordMappingService.cs**: Core agent for mapping grid indices to word pairs, using the optimized word list.
- **Services/IWordMappingService.cs**: Interface for word mapping agent.
- **Program.cs**: API entry point and agent for service configuration.

### Data Flow
1. **Input**: API requests with coordinates or indices.
2. **Processing**: Map input to grid index, retrieve word pair from optimized list.
3. **Output**: Return word pair and metadata to client.

### Automation
- Stateless, deterministic mapping logic.
- Designed for scalable, concurrent API requests.
- Supports integration with mapping frontends and validation tools.

---

## Attribution
- Python agents use data from Peter Norvig, WordNet, ChatGPT, and other sources (see `data/python/README.md`).
- C# agents use the output of the Python pipeline for all word mapping.

---

For detailed co-pilot instructions, see `CO-PILOT-INSTRUCTIONS.md`.
