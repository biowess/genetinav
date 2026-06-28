"""StatsFooter — structured sequence statistics footer widget.

Layout (horizontal, left-to-right):
  Window  60bp  ┊  Cached  0.0Mb  ┊  Window GC  53.3%  ┊
  A  12  T  15  G  18  C  15  ┊  Ready / Loading… / /query  match N/M

The "Window GC" label explicitly scopes the statistic to the visible window,
avoiding any implication of genome-wide GC content.

Each nucleotide count label is coloured using the active palette's base_colors
(or IGV fallback colours when no palette is configured).
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from genetinav.ui_textual.widgets import IGV_COLORS

_SEP = "  ┊  "
_SEP_STYLE = "dim #303050"
_LABEL_STYLE = "dim #7090b0"
_VALUE_STYLE = "bold #c0d8f0"
_STATUS_READY = "dim #506080"
_STATUS_LOADING = "bold #e07c2a"
_STATUS_ERROR = "bold #d94f4f"
_STATUS_SEARCH = "#7ab3e0"


class StatsFooter(Widget):
    """Horizontal stats bar for the sequence viewer."""

    DEFAULT_CSS = """
    StatsFooter {
        height: 1;
        width: 100%;
        background: transparent;
        padding: 0 1;
    }
    """

    window_size: reactive[int] = reactive(60)
    cached_mb: reactive[float] = reactive(0.0)
    gc_pct: reactive[float] = reactive(0.0)
    count_a: reactive[int] = reactive(0)
    count_t: reactive[int] = reactive(0)
    count_g: reactive[int] = reactive(0)
    count_c: reactive[int] = reactive(0)
    status_text: reactive[str] = reactive("Ready")
    search_query: reactive[str] = reactive("")
    match_current: reactive[int] = reactive(0)
    match_total: reactive[int] = reactive(0)
    is_loading: reactive[bool] = reactive(False)
    is_error: reactive[bool] = reactive(False)
    # Active palette colours injected by the parent screen
    palette_colors: reactive[dict] = reactive(dict)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.palette_colors = dict(IGV_COLORS)

    def render(self) -> Text:
        t = Text(no_wrap=True, overflow="ellipsis")
        colors = self.palette_colors if self.palette_colors else IGV_COLORS

        def label(txt: str) -> None:
            t.append(txt, style=_LABEL_STYLE)

        def value(txt: str) -> None:
            t.append(txt, style=_VALUE_STYLE)

        def sep() -> None:
            t.append(_SEP, style=_SEP_STYLE)

        label("Window ")
        value(f"{self.window_size}bp")
        sep()
        label("Cached ")
        value(f"{self.cached_mb:.1f}Mb")
        sep()
        label("Window GC ")
        value(f"{self.gc_pct:.1f}%")
        sep()

        # Per-base counts with active palette colours
        for base, count in (
            ("A", self.count_a),
            ("T", self.count_t),
            ("G", self.count_g),
            ("C", self.count_c),
        ):
            base_color = colors.get(base, IGV_COLORS[base])
            t.append(base, style=f"bold {base_color}")
            t.append(f" {count}  ", style=_VALUE_STYLE)

        sep()

        # Status / search chip
        if self.is_error:
            t.append(self.status_text, style=_STATUS_ERROR)
        elif self.is_loading:
            t.append("Loading…", style=_STATUS_LOADING)
        elif self.search_query:
            t.append(f"/{self.search_query}", style=_STATUS_SEARCH)
            if self.match_total > 0:
                t.append(
                    f"  match {self.match_current}/{self.match_total}",
                    style=_VALUE_STYLE,
                )
            elif self.match_total == 0:
                t.append("  no matches", style=_STATUS_ERROR)
        else:
            t.append("Ready", style=_STATUS_READY)

        return t
