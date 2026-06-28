"""LegendWidget — fixed 1-row nucleotide colour legend.

Shows:  A  T  G  C  N  ●=match  ▐=active
Each letter is coloured using the active palette's base colours (or IGV
defaults). Fits in one terminal row.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from genetinav.ui_textual.widgets import IGV_COLORS, MISMATCH_BG


class LegendWidget(Widget):
    """Single-row legend mapping nucleotide colours to bases."""

    DEFAULT_CSS = """
    LegendWidget {
        height: 1;
        width: 100%;
        background: transparent;
        padding: 0 1;
        color: $text-muted;
    }
    """

    # Active palette colours injected by the parent screen
    palette_colors: reactive[dict] = reactive(dict)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.palette_colors = dict(IGV_COLORS)

    def render(self) -> Text:
        colors = self.palette_colors if self.palette_colors else IGV_COLORS

        t = Text()
        t.append("Legend: ", style="dim #607090")

        entries = [
            ("A", colors.get("A", IGV_COLORS["A"])),
            ("T", colors.get("T", IGV_COLORS["T"])),
            ("G", colors.get("G", IGV_COLORS["G"])),
            ("C", colors.get("C", IGV_COLORS["C"])),
            ("N", colors.get("N", IGV_COLORS["N"])),
        ]
        for base, color in entries:
            t.append("■", style=color)
            t.append(f"{base}  ", style=f"bold {color}")

        t.append("▐", style=f"on {MISMATCH_BG}")
        t.append(" match  ", style="dim")
        t.append("▐", style=f"bold on {MISMATCH_BG}")
        t.append(" active", style="dim")
        return t
