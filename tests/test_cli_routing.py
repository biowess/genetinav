import pytest
from typer.testing import CliRunner

from genetinav.cli import app

runner = CliRunner()

def test_default_no_args():
    result = runner.invoke(app)
    assert result.exit_code == 0
    # No startup echo — the TUI renders directly. Just verify clean exit.

def test_default_with_gene():
    result = runner.invoke(app, ["brca1"])
    assert result.exit_code == 0
    assert "Quick lookup: BRCA1" in result.stdout

def test_search_command():
    result = runner.invoke(app, ["search", "tp53"])
    assert result.exit_code == 0
    assert "Searching for: TP53" in result.stdout

def test_settings_command():
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 0
    # The settings TUI renders; no pre-TUI echo expected.

def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "genetinav v" in result.stdout

def test_no_animation_flag():
    result = runner.invoke(app, ["--no-animation"])
    assert result.exit_code == 0
    assert "Performance mode enabled" in result.stdout

def test_theme_flag():
    # Use a real palette name so the bare-TUI path (no gene) passes cleanly.
    result = runner.invoke(app, ["--theme", "neon_lab"])
    assert result.exit_code == 0
    assert "Theme set to: neon_lab" in result.stdout

def test_species_flag():
    result = runner.invoke(app, ["--species", "human"])
    assert result.exit_code == 0
    assert "Species set to: human" in result.stdout

def test_clear_cache_flag():
    result = runner.invoke(app, ["--clear-cache"])
    assert result.exit_code == 0
    assert "Cache cleared" in result.stdout

def test_clear_history_flag():
    result = runner.invoke(app, ["--clear-history"])
    assert result.exit_code == 0
    assert "History cleared" in result.stdout


# ---------------------------------------------------------------------------
# Validation: invalid --theme / --species are rejected at the CLI boundary
# before GenetinavApp is ever constructed or the database is touched.
# ---------------------------------------------------------------------------

def test_invalid_theme_rejected_by_default_cmd():
    """Bare gene lookup with an unknown theme exits non-zero with a clear error."""
    result = runner.invoke(app, ["BRCA1", "--theme", "not_a_real_theme"])
    assert result.exit_code != 0
    assert "not_a_real_theme" in result.stdout
    assert "Valid themes" in result.stdout
    # The lookup banner must not have been printed — app was never constructed.
    assert "Quick lookup" not in result.stdout


def test_invalid_species_rejected_by_default_cmd():
    """Bare gene lookup with an unknown species exits non-zero with a clear error."""
    result = runner.invoke(app, ["BRCA1", "--species", "not_a_real_species"])
    assert result.exit_code != 0
    assert "not_a_real_species" in result.stdout
    assert "Valid species" in result.stdout
    assert "Quick lookup" not in result.stdout


def test_invalid_theme_rejected_by_search_cmd():
    """'search' subcommand with an unknown theme exits non-zero with a clear error."""
    result = runner.invoke(app, ["search", "TP53", "--theme", "not_a_real_theme"])
    assert result.exit_code != 0
    assert "not_a_real_theme" in result.stdout
    assert "Valid themes" in result.stdout
    assert "Searching for" not in result.stdout


def test_invalid_species_rejected_by_search_cmd():
    """'search' subcommand with an unknown species exits non-zero with a clear error."""
    result = runner.invoke(app, ["search", "TP53", "--species", "not_a_real_species"])
    assert result.exit_code != 0
    assert "not_a_real_species" in result.stdout
    assert "Valid species" in result.stdout
    assert "Searching for" not in result.stdout
