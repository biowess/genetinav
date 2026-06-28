# GenetiNav

**GenetiNav** is a navigational genomics toolkit for exploring, annotating, and querying genomic data through an interactive terminal interface powered by [Rich](https://github.com/Textualize/rich) and [Typer](https://typer.tiangolo.com/).

---

## Features

- 🔬 **Gene lookup** — resolve gene symbols via the [Ensembl REST API](https://rest.ensembl.org/) and display metadata instantly
- 🧬 **Sequence viewer** — scrollable, colour-coded nucleotide display with a coordinate ruler and GC-content statistics
- 📚 **Search history** — automatic session history with configurable retention, filterable and re-openable
- ⭐ **Favourites** — bookmark genes for quick future access
- 🎨 **Theming** — choose from six colour palettes (`classic_bio`, `neon_lab`, `soft_pastel`, `high_contrast`, `monochrome`, `dark_academic`)
- ⚡ **Performance mode** — skip animations for faster/headless usage
- 💾 **Session persistence** — last viewed gene and palette are remembered between sessions
- 🛠️ **Configurable** — all preferences stored in `~/.genetinav/settings.json`

---

## Install

```bash
pip install -e .
```

After installation the `genetinav` command is available on your `$PATH`.

---

## Usage

### Interactive TUI (default)

```bash
genetinav
```

Launches the full interactive terminal UI with a search-first command bar. Type a gene symbol to search, or use slash commands (e.g. `/settings`) to navigate.

### Quick Gene Lookup

```bash
genetinav BRCA1
genetinav brca2
```

Opens the search result for the specified gene directly, then returns to the interactive menu.

### Subcommands

| Command | Description |
|---------|-------------|
| `genetinav search <GENE>` | Pre-fill the search screen with `<GENE>` and launch the TUI |
| `genetinav settings` | Open the settings screen and exit |

---

## Quick-Command Flags (Section 25)

All flags can be combined with any subcommand or used standalone.

| Flag | Description |
|------|-------------|
| `--version` | Print the version string and exit |
| `--no-animation` | Disable all animations / enable performance mode for this session |
| `--theme <NAME>` | Override the active colour palette (e.g. `neon_lab`, `dark_academic`) |
| `--species <NAME>` | Override the default species (e.g. `mouse`, `zebrafish`) |
| `--clear-cache` | Clear the local gene-data cache and exit |
| `--clear-history` | Clear the search history and exit |

### Examples

```bash
# Show version
genetinav --version

# Quick lookup with a specific theme
genetinav BRCA1 --theme neon_lab

# Clear cached gene data
genetinav --clear-cache

# Clear search history
genetinav --clear-history

# Disable animations and use a high-contrast theme
genetinav --no-animation --theme high_contrast

# Search for TP53 in mouse without animations
genetinav search TP53 --species mouse --no-animation

# Open settings in performance mode
genetinav settings --no-animation
```

---

## Command Bar Usage

The command bar is your primary navigation tool. Type a gene symbol (e.g. `BRCA1`) and press Enter to search, or type one of the following slash commands:

| Command | Action |
|---------|--------|
| `/search` | Search for a gene |
| `/history` | View search history |
| `/favorites` | View saved favourites |
| `/settings` | Open settings |
| `/export` | Export current sequence to file |
| `/cache` | Manage local cache |
| `/about` | About screen |
| `/help` | Show help screen |

### Result Screen Shortcuts

| Key | Action |
|-----|--------|
| `o` | Open sequence viewer |
| `v` | Toggle favourite |
| `c` | Copy coordinates |
| `n` | Search another gene |
| `m` | Return to main menu |

### Sequence Viewer Shortcuts

| Key | Action |
|-----|--------|
| `l` | Scroll left (fine step) |
| `r` | Scroll right (fine step) |
| `p` | Page backward |
| `n` | Page forward |
| `q` | Quit viewer / go back |

---

## Configuration

Settings are stored in `~/.genetinav/settings.json` and are edited via the in-app **Settings** screen or directly in the file.

Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `theme` | `classic_bio` | Active colour palette |
| `performance_mode` | `false` | Disable animations |
| `default_species` | `human` | Default species for lookups |
| `default_window_size` | `60` | Sequence window size (bases) |
| `remember_last_session` | `true` | Persist last gene and palette |
| `history_enabled` | `true` | Record search history |
| `cache_enabled` | `true` | Cache API responses locally |

---

## Available Themes

| Name | Description |
|------|-------------|
| `classic_bio` | Traditional green/red/yellow/blue base colours |
| `neon_lab` | Bright neon variant of the classic palette |
| `soft_pastel` | Muted pastel tones for reduced eye strain |
| `high_contrast` | Bold colours on plain backgrounds for accessibility |
| `monochrome` | All bases rendered in white |
| `dark_academic` | Deep, muted scholarly colour scheme |

---

## Built With

| Library | Purpose |
|---------|---------|
| [Rich](https://github.com/Textualize/rich) | Terminal rendering (panels, tables, colours, animations) |
| [Typer](https://typer.tiangolo.com/) | CLI argument parsing and command routing |
| [httpx](https://www.python-httpx.org/) | Async-capable HTTP client for the Ensembl REST API |
| [SQLite](https://sqlite.org/) (stdlib) | Local persistence for cache, history, and favourites |

---

## Data Source

Gene metadata and sequences are retrieved from the **Ensembl REST API** (`https://rest.ensembl.org/`).  
GenetiNav is not affiliated with Ensembl and relies on the public, unauthenticated endpoints.

---

## Status

> **V1 — complete**  
> All 25 feature prompts implemented and tested.

---

## Sequence Viewer — Color & Coordinate Conventions

This section documents the scientific conventions used in the TUI sequence viewer so that accuracy claims are auditable.

### Nucleotide Color Convention (IGV/UCSC Standard)

The viewer uses the nucleotide colour scheme established by **IGV (Integrative Genomics Viewer)** and adopted by the UCSC Genome Browser:

| Base | Color | Hex       | Reference |
|------|-------|-----------|-----------|
| A    | Green | `#3a9e4d` | IGV default |
| T    | Red   | `#d94f4f` | IGV default |
| G    | Orange| `#e07c2a` | Orange substituted for black for dark-terminal visibility |
| C    | Blue  | `#4a7fd4` | IGV default |
| N    | Grey  | `#666666` | Any ambiguous/unknown base |

> **Why orange for G?** IGV originally renders G in a very dark colour (near-black) which is invisible on dark terminal backgrounds. Orange (`#e07c2a`) provides sufficient contrast while remaining visually distinct from A (green), T (red), and C (blue).

These colours are defined in `src/genetinav/ui_textual/widgets/__init__.py` as `IGV_COLORS` and are the single source of truth across all widgets (ruler, sequence track, legend, stats footer).

### Coordinate System

- **1-based, closed interval**: Coordinates are displayed as `chrN:start–end` where both start and end are 1-based genomic positions (inclusive). This matches the convention used by Ensembl, UCSC, and IGV.
- **Chromosome context is always shown**: The chromosome identifier is displayed in the card border title and the minimap, even when navigating within a single chromosome, to avoid ambiguity.
- **Example**: `BRCA1 — chr17:43,044,295–43,044,354 (+)` means bases 43,044,295 through 43,044,354 on chromosome 17, forward strand.

### GC Content Scope

The **"Window GC"** statistic in the stats footer is computed exclusively from the currently visible sequence window, not from the full gene sequence or chromosome. This is labelled explicitly as `Window GC` to prevent any implication of genome-wide or gene-wide GC content.

Formula: `GC% = (count(G) + count(C)) / window_size × 100`

### Mismatch / Search Highlight Convention

| Display Style | Meaning |
|---------------|---------|
| Bold + underline on base colour | Active search match (current position) |
| Bold on purple background (`#5a1a5a`) | Passive search match (other occurrences in window) |
| Base colour on purple background | Reference/variant mismatch (if mismatch data provided) |

### Strand Direction

The strand direction (`+` or `−`) of the gene is shown in the card border title and appended to the sequence track. The `c` key toggles **reverse complement** display in-place; the original forward-strand sequence is never discarded, only the rendered view changes.

### Minimap

The minimap at the top-right of the card uses filled (`█`) and outline (`░`) block characters to show the fraction of the approximate chromosome length (default: 300 Mbp) covered by the current viewport. The coordinate shown is the absolute 1-based start position of the viewport.

---

## License

MIT License — see `LICENSE` for details.
