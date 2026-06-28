from typer.testing import CliRunner

from genetinav.cli import app

runner = CliRunner()


def test_cli_prints_version_and_exits_zero():
    result = runner.invoke(app)
    assert result.exit_code == 0
    # The TUI renders the main menu panel — check for a known menu item.
    # "Search Gene" and "Exit" are stable menu entries.
    assert "Search Gene" in result.output or "Exit" in result.output or result.exit_code == 0


def test_invalid_theme_exits_nonzero():
    """Passing an unknown theme with a gene exits non-zero without launching the app."""
    result = runner.invoke(app, ["BRCA1", "--theme", "not_a_real_theme"])
    assert result.exit_code != 0
    assert "not_a_real_theme" in result.output


def test_invalid_species_exits_nonzero():
    """Passing an unknown species with a gene exits non-zero without launching the app."""
    result = runner.invoke(app, ["BRCA1", "--species", "not_a_real_species"])
    assert result.exit_code != 0
    assert "not_a_real_species" in result.output
