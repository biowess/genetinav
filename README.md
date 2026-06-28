<p align="center">
  <img src="https://github.com/biowess/genetinav/blob/main/docs/genetinav.png" alt="genetinav">
</p>

A terminal-based genomics toolkit for gene lookup, DNA sequence exploration, and genomic coordinate navigation.  
Built with Textual and Typer, powered by the public Ensembl REST API.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat)](https://www.python.org/)
[![Textual](https://img.shields.io/badge/Textual-0.49.0+-brightgreen?style=flat)](https://textual.textualize.io/)
[![Typer](https://img.shields.io/badge/Typer-0.12+-orange?style=flat)](https://typer.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Custom%20Source--Available%201.0-lightgrey?style=flat)](LICENSE)

Type a gene symbol to retrieve its metadata, then drop into a colour-coded, scrollable sequence viewer with motif search, reverse-complement display, and live gene-boundary detection — all from your terminal.

## Features

- **Gene lookup** – resolve gene symbols via the Ensembl REST API (human, mouse, rat, zebrafish)
- **Interactive sequence viewer** – scrollable, colour-coded nucleotide track with coordinate ruler, GC-content sparkline, minimap, and stats footer
- **Rich navigation** – base-by-base and page-by-page scrolling, jump-to-coordinate or gene, motif search with next/prev match, zoom, and back/forward history
- **Reverse-complement toggle** – flip the display in place without losing position
- **Dynamic gene-boundary detection** – the viewer automatically relabels itself as you scroll across gene/intergenic boundaries
- **Search history** – automatically recorded, capped at 200 entries, browsable and re-openable
- **Favourites** – bookmark genes for quick future access
- **Theming** – 10 built-in dark colour themes, each with its own DNA base-colour palette
- **Local caching** – SQLite-backed response cache plus an in-memory chunked sequence cache with background prefetching
- **Export** – Markdown, JSON, or FASTA (genomic / transcript / CDS) export of the current gene
- **Open in Ensembl** – jump straight to the gene’s Ensembl page in your browser
- **Command palette** – fuzzy-filterable command search, global and viewer-aware
- **Performance mode** – disable animations for a snappier or headless-friendly session
- **Configurable** – all preferences stored in `~/.genetinav/settings.json`

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/biowess/genetinav.git
cd genetinav
pip install -e .
```

This installs the `genetinav` console command on your `$PATH`.  
Dependencies (typer, httpx, textual) are declared in `pyproject.toml` and installed automatically.

## Usage

Launch the interactive TUI:

```bash
genetinav
```

Opens the home screen with a search bar. Type a gene symbol and press Enter, or use a `/command` to navigate directly.

Quick gene lookup:

```bash
genetinav BRCA1
genetinav brca2
```

Performs an immediate lookup inside the TUI.

### Subcommands

| Command                  | Description                              |
|--------------------------|------------------------------------------|
| `genetinav search <GENE>`| Launch the TUI and look up `<GENE>`      |
| `genetinav settings`     | Open the Settings screen directly        |

### Flags

| Flag                 | Description                                               |
|----------------------|-----------------------------------------------------------|
| `--version`          | Print the version string and exit                         |
| `--no-animation`     | Disable animations / enable performance mode              |
| `--theme <NAME>`     | Override the active colour theme for this session         |
| `--species <NAME>`   | Override the default species for this session             |
| `--clear-cache`      | Clear the local gene/sequence response cache and exit     |
| `--clear-history`    | Clear the search history and exit                         |

```bash
# Quick lookup with a specific theme
genetinav BRCA1 --theme midnight_genome

# Disable animations and set default species to mouse
genetinav --no-animation --species mouse

# Clear cached data
genetinav --clear-cache
genetinav --clear-history
```

### In-app navigation

From the home screen, type a gene symbol or a slash command:

| Command       | Action                           |
|---------------|----------------------------------|
| `/settings`   | Open Settings                    |
| `/help`       | Show keybinding reference        |
| `/about`      | About GenetiNav (and license)    |
| `/history`    | View search history              |
| `/recent`     | View search history              |
| `/favorites`  | View saved favourites            |
| `/themes`     | List available colour themes     |
| `/theme`      | Prompt to switch active theme    |

### Result screen keys

| Key   | Action                                     |
|-------|--------------------------------------------|
| `o`   | Open the sequence viewer                   |
| `v`   | Toggle favourite                           |
| `c`   | Show / copy genomic coordinates            |
| `n`   | Start a new search                         |
| `m`   | Open the menu (Export, Open in Ensembl)    |
| `q` / `Esc` | Back to home                        |

### Sequence viewer keys

| Key                | Action                                              |
|--------------------|-----------------------------------------------------|
| `←` / `→`          | Scroll 1 base pair                                  |
| `↑` / `↓`, `PgUp` / `PgDn` | Scroll one full window                   |
| `Home` / `End`     | Jump to sequence start / end                        |
| `g`                | Go to a coordinate (e.g. `chr9:5057799`) or gene    |
| `/`                | Search for a DNA motif                              |
| `n` / `N`          | Next / previous match                               |
| `c`                | Toggle reverse-complement display                   |
| `Ctrl+G`           | Toggle the GC-content track                         |
| `<` / `>`          | Navigate back / forward in viewer history           |
| `+` / `-`          | Zoom window size in / out                           |
| `Ctrl+P`           | Open the command palette                            |
| `q` / `Esc`        | Close the viewer                                    |

## Project Structure

```
genetinav/
├── pyproject.toml
├── LICENSE
├── README.md
├── src/genetinav/
│   ├── cli.py                  # Typer CLI entry point
│   ├── textual_app.py          # GenetinavTUI — the Textual App
│   ├── gene_service.py         # Gene lookup, sequence + transcript retrieval
│   ├── api_client.py           # EnsemblClient — Ensembl REST API calls
│   ├── chunk_cache.py          # In-memory chunked sequence cache + prefetcher
│   ├── cache.py / db.py        # SQLite-backed cache + schema
│   ├── history.py / favorites.py
│   ├── models.py               # GeneRecord and other dataclasses
│   ├── navigation_history.py   # Back/forward stack for the viewer
│   ├── sequence.py             # Windowing, GC%, base counts, ruler ticks
│   ├── settings.py             # Settings load/save (~/.genetinav/settings.json)
│   ├── themes.py               # UI + DNA base colour theme registry
│   ├── utils/                  # Errors, validation, export (FASTA)
│   └── ui_textual/             # Screens, modals, and widgets
│       ├── home_screen.py
│       ├── result_screen.py
│       ├── sequence_viewer_screen.py
│       ├── *_modal.py          # settings / history / favorites / help / about / menu
│       └── widgets/            # ruler, sequence track, GC track, minimap, legend, stats
└── tests/                      # pytest suite
```

## Technologies

| Library   | Purpose                                                |
|-----------|--------------------------------------------------------|
| Textual   | Terminal UI framework (screens, widgets, event loop)   |
| Typer     | CLI argument parsing and subcommands                   |
| httpx     | HTTP client for the Ensembl REST API                   |
| SQLite    | Local persistence for cache, history, and favourites   |

## Export Formats

From the result screen menu (`m` → Export):

| Format            | Filename                                | Contents                              |
|-------------------|-----------------------------------------|---------------------------------------|
| Markdown          | `{SYMBOL}_export.md`                    | Symbol, species, location, summary    |
| JSON              | `{SYMBOL}_export.json`                  | Full GeneRecord dump                  |
| FASTA – Genomic   | `{SYMBOL}_genomic_{timestamp}.fasta`    | The gene’s chromosomal region         |
| FASTA – Transcript| `{SYMBOL}_transcript_{timestamp}.fasta` | Canonical transcript cDNA             |
| FASTA – CDS       | `{SYMBOL}_cds_{timestamp}.fasta`        | Canonical CDS (falls back to cDNA)    |

## Configuration

Settings are stored in `~/.genetinav/settings.json` and can be edited through the in-app Settings screen (`/settings`) or directly.  
The local database lives at `~/.genetinav/genetinav.db`.

| Setting               | Default           | Description                                 |
|-----------------------|-------------------|---------------------------------------------|
| `theme`               | `obsidian_helix`  | Active colour theme                         |
| `history_enabled`     | `true`            | Record search history                       |
| `cache_enabled`       | `true`            | Cache Ensembl API responses locally         |
| `default_window_size` | `60`              | Sequence viewer window size (bases)         |
| `default_species`     | `human`           | Default species for lookups                 |
| `ruler_interval`      | `10`              | Spacing between ruler tick labels           |

## Available Themes

Ten dark, biologically-themed palettes, each defining both the UI chrome and the DNA base colours used by the sequence viewer:

- obsidian_helix
- midnight_genome
- carbon_strand
- void_polymer
- deep_cell
- nucleic_night
- graphene_dark
- helix_abyss
- synthetic_strand
- black_helix_neon

List them at any time with `/themes`, or switch instantly with `/theme`.

## Data Source

Gene metadata and sequence data are retrieved from the Ensembl REST API (`https://rest.ensembl.org/`) using public, unauthenticated endpoints.  
GenetiNav is not affiliated with Ensembl.

## Screenshots

*Add screenshots or terminal recordings of GenetiNav below.*

| Home Screen              | Result Screen              | Sequence Viewer              |
|--------------------------|----------------------------|------------------------------|
| Home screen placeholder  | Result screen placeholder  | Sequence viewer placeholder  |

## Roadmap

These are potential future directions, not yet implemented:

- [ ] Wire up reserved settings (high contrast, monochrome, animation toggles) to live Settings controls
- [ ] Persist CLI `--theme` / `--species` overrides back to `settings.json`
- [ ] Automatic retry/backoff for Ensembl API rate limiting and transient network errors
- [ ] Configurable export destination directory
- [ ] Disk-persisted sequence and overlap caches for faster cold starts
- [ ] Broader species support beyond human, mouse, rat, and zebrafish

## License

Custom Source-Available License 1.0 – Copyright © 2026 BIOWESS.  
You may view, clone, run, and modify this software for personal or educational use, and share non-commercial educational derivatives with attribution. Commercial use, resale, rebranding, or hosting as a paid service is not permitted without prior written permission. See `LICENSE` for the full terms.

## Credits & Acknowledgements

Gene and sequence data courtesy of the Ensembl project.  
Built with Textual and Typer by Textualize.  
Nucleotide colour convention inspired by IGV and the UCSC Genome Browser.
