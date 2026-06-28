"""GcTrackWidget — per-block GC content bar rendered as block art.

Renders a single row of Unicode block-height characters:
  ▁ ▂ ▃ ▄ ▅ ▆ ▇ █  (proportional to GC% in each 10bp block)

Each block covers `block_size` bases. The bar is coloured by GC level:
  < 30%  → dim blue   (AT-rich)
  30–60% → accent teal
  > 60%  → amber      (GC-rich)
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

_BLOCKS = " ▁▂▃▄▅▆▇█"


def _block_char(gc_frac: float) -> str:
    idx = min(8, int(gc_frac * 8 + 0.5))
    return _BLOCKS[idx]


def _block_style(gc_frac: float) -> str:
    if gc_frac < 0.30:
        return "dim #4a7fd4"
    if gc_frac > 0.60:
        return "#e07c2a"
    return "#3abaaa"


class GcTrackWidget(Widget):
    """Per-block GC content bar (block-art characters)."""

    DEFAULT_CSS = """
    GcTrackWidget {
        height: 1;
        width: 100%;
        background: transparent;
        padding: 0 1;
    }
    """

    window_seq: reactive[str] = reactive("", layout=True)
    block_size: reactive[int] = reactive(10)

    def __init__(self, window_seq: str = "", block_size: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self.window_seq = window_seq
        self.block_size = block_size

    def render(self) -> Text:
        seq = (self.window_seq or "").upper()
        bs = max(1, self.block_size)
        result = Text()
        minor = 10

        for block_idx, block_start in enumerate(range(0, len(seq), bs)):
            # Pipe separator (mirrors sequence track spacing)
            if block_idx > 0 and block_start % minor == 0:
                result.append("│", style="dim #404060")

            block = seq[block_start : block_start + bs]
            if not block:
                break
            gc = sum(1 for b in block if b in "GC")
            frac = gc / len(block)
            char = _block_char(frac)
            style = _block_style(frac)
            # Each block covers `bs` base columns — pad to fill them
            result.append(char * bs, style=style)

        return result
