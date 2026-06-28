"""Command-line interface for GenetiNav.

Quick-command flags (spec Section 25):
  genetinav                       # launch interactive TUI
  genetinav <GENE>                # quick gene lookup, then exit
  genetinav search <GENE>         # launch TUI pre-filled with GENE
  genetinav settings              # open settings screen then exit
  genetinav --no-animation        # disable animations for this session
  genetinav --theme <NAME>        # override active palette for this session
  genetinav --species <NAME>      # override default species for this session
  genetinav --clear-cache         # clear local gene cache then exit
  genetinav --clear-history       # clear search history then exit
  genetinav --version             # print version and exit
"""

import typer
from typing import Optional

from genetinav import __version__
from genetinav.cache import CacheManager
from genetinav.history import HistoryManager
from genetinav.db import get_connection, initialize_schema


class DefaultGroup(typer.core.TyperGroup):
    """Allow a bare positional argument to be handled as the 'default' sub-command."""

    def resolve_command(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args.insert(0, "default")
        return super().resolve_command(ctx, args)


app = typer.Typer(cls=DefaultGroup)


def version_callback(value: bool):
    if value:
        typer.echo(f"genetinav v{__version__}")
        raise typer.Exit()


def _build_overrides(
    no_animation: bool,
    theme: Optional[str],
    species: Optional[str],
) -> dict:
    """Return a partial settings dict reflecting CLI flag overrides."""
    overrides: dict = {}
    if no_animation:
        overrides["performance_mode"] = True
        overrides["animations_enabled"] = False
        overrides["splash_animation_enabled"] = False
    if theme:
        overrides["theme"] = theme
    if species:
        overrides["default_species"] = species
    return overrides





def _validate_cli_overrides(theme: Optional[str], species: Optional[str]) -> None:
    """Validate --theme and --species values at the CLI boundary.

    Prints a user-friendly error and raises ``typer.Exit(code=1)`` when an
    invalid value is supplied, so the error surfaces before GenetinavApp is
    ever constructed or the database is touched.
    """
    if theme is not None:
        from genetinav.themes import list_ui_theme_names
        valid_themes = list_ui_theme_names()
        if theme not in valid_themes:
            typer.echo(
                f"Error: '{theme}' is not a valid theme. "
                f"Valid themes: {', '.join(valid_themes)}"
            )
            raise typer.Exit(code=1)

    if species is not None:
        from genetinav.utils.validation import DEFAULT_ALLOWED_SPECIES
        valid_species = DEFAULT_ALLOWED_SPECIES
        normalized = species.strip().lower()
        if normalized not in valid_species:
            typer.echo(
                f"Error: '{species}' is not a valid species. "
                f"Valid species: {', '.join(valid_species)}"
            )
            raise typer.Exit(code=1)


def _run_gene_cmd(
    gene: str,
    no_animation: bool,
    theme: Optional[str],
    species: Optional[str],
    echo_message: str,
) -> None:
    """Shared implementation for default_cmd and search_cmd.

    Validates overrides, emits the command-specific banner, constructs the
    app, and runs the quick-lookup flow.  Each caller supplies its own
    *echo_message* ("Quick lookup: {gene}" vs "Searching for: {gene}").
    """
    _validate_cli_overrides(theme, species)
    typer.echo(echo_message)
    overrides = _build_overrides(no_animation, theme, species)
    from genetinav.settings import load_settings
    from genetinav.textual_app import GenetinavTUI
    
    settings = load_settings()
    settings.update(overrides)
    tui = GenetinavTUI(settings=settings, initial_query=gene)
    tui.run()
    typer.echo("Session terminated gracefully. Goodbye!")


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
    no_animation: bool = typer.Option(False, "--no-animation", help="Disable animations for this session"),
    theme: Optional[str] = typer.Option(None, "--theme", help="Override active colour palette"),
    species: Optional[str] = typer.Option(None, "--species", help="Override default species"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Clear the local gene cache then exit"),
    clear_history: bool = typer.Option(False, "--clear-history", help="Clear the search history then exit"),
) -> None:
    """GenetiNav — navigational genomics toolkit."""

    # --clear-cache / --clear-history are handled first so they can be combined
    # with each other (and still print their confirmation messages) before any
    # interactive UI is launched.
    if clear_cache:
        conn = get_connection()
        initialize_schema(conn)
        cache_mgr = CacheManager(conn)
        cache_mgr.clear()
        conn.close()
        typer.echo("Cache cleared")

    if clear_history:
        conn = get_connection()
        initialize_schema(conn)
        history_mgr = HistoryManager(conn)
        history_mgr.clear()
        conn.close()
        typer.echo("History cleared")

    # If a data-clearing flag was used without a subcommand, exit cleanly.
    if clear_cache or clear_history:
        if ctx.invoked_subcommand is None:
            return

    # Launch the interactive TUI when no subcommand was given.
    # Informational flag summaries are printed *after* the session ends so
    # they are not immediately scrolled away by the splash screen.
    if ctx.invoked_subcommand is None:
        overrides = _build_overrides(no_animation, theme, species)
        from genetinav.settings import load_settings
        from genetinav.textual_app import GenetinavTUI
        settings = load_settings()
        settings.update(overrides)
        tui = GenetinavTUI(settings=settings)
        tui.run()
        typer.echo("Session terminated gracefully. Goodbye!")

        # Print flag confirmations after the TUI exits so they remain visible.
        if no_animation:
            typer.echo("Performance mode enabled")
        if theme:
            typer.echo(f"Theme set to: {theme}")
        if species:
            typer.echo(f"Species set to: {species}")


@app.command("default", hidden=True)
def default_cmd(
    gene: str,
    no_animation: bool = typer.Option(False, "--no-animation"),
    theme: Optional[str] = typer.Option(None, "--theme"),
    species: Optional[str] = typer.Option(None, "--species"),
) -> None:
    """Quick lookup: launch TUI pre-filled with GENE."""
    _run_gene_cmd(
        gene=gene,
        no_animation=no_animation,
        theme=theme,
        species=species,
        echo_message=f"Quick lookup: {gene.upper()}",
    )


@app.command("search")
def search_cmd(
    gene: str,
    no_animation: bool = typer.Option(False, "--no-animation"),
    theme: Optional[str] = typer.Option(None, "--theme"),
    species: Optional[str] = typer.Option(None, "--species"),
) -> None:
    """Search for a GENE in the interactive TUI."""
    _run_gene_cmd(
        gene=gene,
        no_animation=no_animation,
        theme=theme,
        species=species,
        echo_message=f"Searching for: {gene.upper()}",
    )


@app.command("settings")
def settings_cmd(
    no_animation: bool = typer.Option(False, "--no-animation"),
    theme: Optional[str] = typer.Option(None, "--theme"),
) -> None:
    """Open the settings screen."""
    overrides = _build_overrides(no_animation, theme, None)
    from genetinav.settings import load_settings
    from genetinav.textual_app import GenetinavTUI
    
    settings = load_settings()
    settings.update(overrides)
    tui = GenetinavTUI(settings=settings, initial_screen="settings")
    tui.run()
    typer.echo("Session terminated gracefully. Goodbye!")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
