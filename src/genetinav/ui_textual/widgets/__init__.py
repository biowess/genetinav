"""Shared IGV nucleotide color constants and helpers for sequence viewer widgets.

IGV / UCSC standard (used as fallback when palette has no custom base_colors):
  A → green   (#3a9e4d)
  T → red     (#d94f4f)
  G → orange  (#e07c2a)  — orange replaces black for dark-terminal visibility
  C → blue    (#4a7fd4)
  N → grey    (#666666)

Mismatch highlight (inverse-video background):
  #5a1a5a  — deep purple, WCAG-contrast-safe on dark backgrounds
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

# ── IGV nucleotide hex colors (canonical fallback) ────────────────────────────
IGV_COLORS: dict[str, str] = {
    "A": "#3a9e4d",
    "T": "#d94f4f",
    "G": "#e07c2a",
    "C": "#4a7fd4",
    "N": "#666666",
}

MISMATCH_BG = "#5a1a5a"
ACTIVE_MATCH_STYLE = "bold underline"


def igv_colorize(base: str) -> str:
    """Return Rich style string for *base* using the IGV convention.

    Returns the N colour for any unrecognised character so the sequence
    track never raises on degenerate IUPAC codes.
    """
    return IGV_COLORS.get(base.upper(), IGV_COLORS["N"])


def get_palette_colors(app: "App | None" = None) -> dict[str, str]:
    """Resolve the active palette's base_colors to hex strings.

    Reads the current theme from ``app.settings["theme"]``, looks up the
    corresponding :class:`~genetinav.themes.UITheme`, and returns the DNA
    base colors.

    Falls back to :data:`IGV_COLORS` if:
    - *app* is ``None``.
    - The theme key is missing or unknown.

    The returned dict always contains all five keys: A, T, G, C, N.
    """
    if app is None:
        return dict(IGV_COLORS)

    try:
        from genetinav.themes import get_ui_theme, DEFAULT_UI_THEME

        theme_name: str = getattr(app, "settings", {}).get("theme", DEFAULT_UI_THEME)
        try:
            theme = get_ui_theme(theme_name)
        except ValueError:
            return dict(IGV_COLORS)

        return {
            "A": theme.base_a,
            "T": theme.base_t,
            "G": theme.base_g,
            "C": theme.base_c,
            "N": theme.base_n,
        }
    except Exception:
        return dict(IGV_COLORS)


__all__ = [
    "IGV_COLORS",
    "MISMATCH_BG",
    "ACTIVE_MATCH_STYLE",
    "igv_colorize",
    "get_palette_colors",
]
