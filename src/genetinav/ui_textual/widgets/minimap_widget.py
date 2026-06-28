"""MinimapWidget — chromosomal position minimap with viewport indicator.

Renders a single-line minimap:
  chr9  ░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░░░░  5,057,799

  █ blocks = current viewport
  ░ blocks = unviewed chromosome
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

_TRACK_STYLE = "dim #404060"
_VIEWPORT_STYLE = "#7ab3e0"
_LABEL_STYLE = "bold #a0c0ff"
_COORD_STYLE = "dim #7090b0"


class MinimapWidget(Widget):
    """Single-row minimap showing viewport position within the full chromosome."""

    DEFAULT_CSS = """
    MinimapWidget {
        height: 1;
        width: 1fr;
        background: transparent;
        content-align: right middle;
    }
    """

    chromosome: reactive[str] = reactive("chr?")
    total_len: reactive[int] = reactive(300_000_000)
    viewport_start: reactive[int] = reactive(0)
    viewport_end: reactive[int] = reactive(60)

    def __init__(
        self,
        chromosome: str = "chr?",
        total_len: int = 300_000_000,
        viewport_start: int = 0,
        viewport_end: int = 60,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.chromosome = chromosome
        self.total_len = total_len
        self.viewport_start = viewport_start
        self.viewport_end = viewport_end

    # ── render ────────────────────────────────────────────────────────────────

    def render(self) -> Text:
        total = max(self.total_len, 1)
        vstart = max(0, self.viewport_start)
        vend = min(total, self.viewport_end)

        # Track width — leave room for label + coordinate
        track_width = 32
        ratio_start = vstart / total
        ratio_end = vend / total
        fill_start = int(ratio_start * track_width)
        fill_end = max(fill_start + 1, int(ratio_end * track_width))
        fill_end = min(fill_end, track_width)

        t = Text()
        t.append(f"{self.chromosome}  ", style=_LABEL_STYLE)
        t.append("░" * fill_start, style=_TRACK_STYLE)
        t.append("█" * (fill_end - fill_start), style=_VIEWPORT_STYLE)
        t.append("░" * (track_width - fill_end), style=_TRACK_STYLE)
        t.append(f"  {vstart:,}", style=_COORD_STYLE)
        return t
