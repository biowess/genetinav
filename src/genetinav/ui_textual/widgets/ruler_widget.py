"""RulerWidget — per-base genomic ruler with tick marks.

Renders two rows:
  Row 1 (ticks):   ┊ at every minor interval (10bp), ┃ at every major (50bp)
  Row 2 (numbers): coordinate label left-aligned under each tick

Column alignment mirrors SequenceTrackWidget exactly:
  - one character per base
  - a │ separator inserted after every 10th base
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class RulerWidget(Widget):
    """Genomic position ruler that aligns column-for-column with the sequence track."""

    DEFAULT_CSS = """
    RulerWidget {
        height: 2;
        width: 100%;
        color: $text-muted;
        background: transparent;
        padding: 0 1;
    }
    """

    start_coord: reactive[int] = reactive(1, layout=True)
    window_size: reactive[int] = reactive(60, layout=True)
    minor_interval: reactive[int] = reactive(10, layout=True)
    major_interval: reactive[int] = reactive(50, layout=True)

    def __init__(
        self,
        start_coord: int = 1,
        window_size: int = 60,
        minor_interval: int = 10,
        major_interval: int = 50,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.start_coord = start_coord
        self.window_size = window_size
        self.minor_interval = minor_interval
        self.major_interval = major_interval

    # ── render ────────────────────────────────────────────────────────────────

    def render(self) -> Text:
        """Build the two-line tick + number ruler aligned to the sequence track."""
        ws = self.window_size
        minor = self.minor_interval
        major = self.major_interval
        start = self.start_coord

        # Total visual width = ws bases + (ws-1)//10 separators
        sep_count = (ws - 1) // minor
        total_cols = ws + sep_count

        tick_chars: list[str] = [" "] * total_cols
        num_chars: list[str] = [" "] * total_cols

        def _visual_col(base_idx: int) -> int:
            """Convert 0-based base index to visual column (accounting for separators)."""
            return base_idx + (base_idx // minor)

        for base_idx in range(ws):
            abs_coord = start + base_idx
            vis_col = _visual_col(base_idx)

            if (abs_coord - 1) % major == 0:
                tick_chars[vis_col] = "┃"
            elif (abs_coord - 1) % minor == 0:
                tick_chars[vis_col] = "┊"

            if (abs_coord - 1) % minor == 0:
                label = str(abs_coord)
                for k, ch in enumerate(label):
                    if vis_col + k < total_cols:
                        num_chars[vis_col + k] = ch

        # Pipe-separator positions (same as sequence track)
        for base_idx in range(minor, ws, minor):
            sep_col = base_idx + (base_idx // minor) - 1
            if 0 <= sep_col < total_cols:
                if tick_chars[sep_col] == " ":
                    tick_chars[sep_col] = " "  # keep blank between ticks
                if num_chars[sep_col] == " ":
                    num_chars[sep_col] = " "

        tick_line = "".join(tick_chars)
        num_line = "".join(num_chars)

        t = Text()
        # Tick row — style major vs minor differently
        for i, ch in enumerate(tick_line):
            if ch == "┃":
                t.append(ch, style="bold #a0c0ff")
            elif ch == "┊":
                t.append(ch, style="dim #607090")
            else:
                t.append(ch)
        t.append("\n")
        # Number row
        t.append(num_line, style="dim #7090b0")
        return t
