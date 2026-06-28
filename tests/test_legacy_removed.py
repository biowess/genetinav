"""Tests verifying the clean removal of legacy UI components."""

import pytest
from typer.testing import CliRunner
from genetinav.cli import app

runner = CliRunner()

def test_legacy_ui_modules_removed():
    """Verify that the entire legacy ui package is no longer importable."""
    with pytest.raises(ImportError):
        import genetinav.ui

def test_classic_ui_flag_removed():
    """Verify that --classic-ui flag is no longer accepted."""
    result = runner.invoke(app, ["--classic-ui"])
    assert result.exit_code != 0
    assert "No such option" in result.output and "--classic-ui" in result.output
