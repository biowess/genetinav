"""SequenceTrackWidget — coloured nucleotide sequence display.

Uses IGV colour convention by default; palette_colors overrides per active theme:
  A = green  T = red  G = orange  C = blue  N = grey

Pipe separators │ are inserted after every 10th base, matching RulerWidget.

Mismatch bases (where provided) are rendered with inverse-video background.
Active search match is bold + underline on top of the base colour.
Strand direction (+ / −) is shown at the right edge.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from genetinav.ui_textual.widgets import (
    IGV_COLORS,
    MISMATCH_BG,
    ACTIVE_MATCH_STYLE,
    igv_colorize,
)

_PIPE_STYLE = "dim #404060"
_STRAND_STYLE = "bold #a0c0ff"


class SequenceTrackWidget(Widget):
    """Renders one line of coloured nucleotides with search highlighting."""

    DEFAULT_CSS = """
    SequenceTrackWidget {
        height: 1;
        width: 100%;
        background: transparent;
        padding: 0 1;
    }
    """

    window_seq: reactive[str] = reactive("", layout=True)
    search_query: reactive[str] = reactive("")
    matches_in_window: reactive[list] = reactive(list)
    active_match: reactive[int | None] = reactive(None)
    strand: reactive[str] = reactive("+")
    reverse_complement: reactive[bool] = reactive(False)
    mismatch_positions: reactive[set] = reactive(set)
    # Active palette colours injected by the parent screen
    palette_colors: reactive[dict] = reactive(dict)

    def __init__(
        self,
        window_seq: str = "",
        strand: str = "+",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.window_seq = window_seq
        self.strand = strand
        self.palette_colors = dict(IGV_COLORS)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _rev_comp(self, seq: str) -> str:
        comp = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}
        return "".join(comp.get(b.upper(), "N") for b in reversed(seq))

    def _base_color(self, base: str) -> str:
        """Return hex color for *base* using active palette or IGV fallback."""
        colors = self.palette_colors if self.palette_colors else IGV_COLORS
        return colors.get(base.upper(), colors.get("N", IGV_COLORS["N"]))

    # ── render ────────────────────────────────────────────────────────────────

    def render(self) -> Text:
        seq = self.window_seq or ""
        if self.reverse_complement:
            seq = self._rev_comp(seq)

        query_len = len(self.search_query) if self.search_query else 0

        # Build sets of highlighted indices
        match_indices: set[int] = set()
        active_indices: set[int] = set()
        if self.search_query and self.matches_in_window:
            for start_idx in self.matches_in_window:
                for k in range(query_len):
                    if start_idx + k < len(seq):
                        match_indices.add(start_idx + k)
                        if self.active_match is not None and start_idx == self.active_match:
                            active_indices.add(start_idx + k)

        result = Text()
        minor = 10

        for i, base in enumerate(seq):
            # Pipe separator
            if i > 0 and i % minor == 0:
                result.append("│", style=_PIPE_STYLE)

            base_color = self._base_color(base)

            if i in active_indices:
                # Active match: bold + underline + base color
                result.append(base, style=f"bold underline {base_color}")
            elif i in match_indices:
                # Passive match: reverse-video mismatch background
                result.append(base, style=f"bold on {MISMATCH_BG}")
            elif i in self.mismatch_positions:
                result.append(base, style=f"{base_color} on {MISMATCH_BG}")
            else:
                result.append(base, style=f"bold {base_color}")

        # Strand indicator
        if seq:
            strand_char = "+" if self.strand == "+" else "−"
            rc_tag = " ↺" if self.reverse_complement else ""
            result.append(f"  [{strand_char}{rc_tag}]", style=_STRAND_STYLE)

        return result
