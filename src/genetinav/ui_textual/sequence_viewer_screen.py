"""Sequence Viewer Screen for GenetiNav Textual app.

Visual hierarchy (single card):
  ┌─ viewer-card  [GENE — chrN:start–end  (+)] ──────────────────────────────┐
  │  chrN  ░░░░░████░░░░░░░░░░░░░░░░  5,057,799            match 3/7         │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  ┊         ┃         ┊                                                    │  ← RulerWidget (ticks)
  │  5,057,800          5,057,850                                             │  ← RulerWidget (numbers)
  │  ATGCATGCAT│GCATGCATGC│ATGCATGCAT│GCATGCATGC│ATGCATGCAT│GCATGCATGC [+] │  ← SequenceTrackWidget
  │  ▁▁▄▆█▄▄▁▁│▂▃▄▅▆▅▃▂▁▁│                                                  │  ← GcTrackWidget
  │  ─────────────────────────────────────────────────────────────────────── │
  │  ■A  ■T  ■G  ■C  ■N  ▐ match  ▐ active                                  │  ← LegendWidget
  │  Window 60bp  ┊  Cached 0.0Mb  ┊  Window GC 53.3%  ┊  A 12  T 15 …     │  ← StatsFooter
  └───────────────────────────────────────────────────────────────────────── ┘

Data model:
  SequenceViewerController from genetinav.ui_textual.sequence_viewer_controller
  SequenceProxy defined inline
  NavigationHistory from genetinav.navigation_history
  GeneRecord from genetinav.models

Scientific conventions:
  - Coordinates are 1-based genomic (chrN:start–end).
  - Nucleotide colours follow the active palette (IGV/UCSC standard by default).
  - 'Window GC' is computed from the visible window only — not the whole sequence.
  - Strand (+/−) is shown on the sequence track and in the card border title.
"""

from __future__ import annotations

import re
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, Rule, Static
from textual import events

from genetinav.navigation_history import NavigationHistory
from genetinav.sequence import base_counts, gc_percentage
from genetinav.ui_textual.base_screen import BaseScreen
from genetinav.ui_textual.sequence_viewer_controller import SequenceViewerController
from genetinav.ui_textual.widgets import get_palette_colors
from genetinav.ui_textual.widgets.gc_track_widget import GcTrackWidget
from genetinav.ui_textual.widgets.legend_widget import LegendWidget
from genetinav.ui_textual.widgets.minimap_widget import MinimapWidget
from genetinav.ui_textual.widgets.ruler_widget import RulerWidget
from genetinav.ui_textual.widgets.sequence_track_widget import SequenceTrackWidget
from genetinav.ui_textual.widgets.stats_footer_widget import StatsFooter

# Path to companion TCSS file
_TCSS_PATH = Path(__file__).parent / "sequence_viewer.tcss"

# Error message shown when a sequence fetch returns no data
_SEQ_UNAVAILABLE = "⚠ Sequence Unavailable at this Range"


# ── SequenceProxy ────────────────────────────────────────────────────────────


class SequenceProxy:
    """Lazy genomic sequence proxy that fetches chunks on demand.

    Satisfies the ``str``-like interface expected by
    :class:`~genetinav.ui_textual.sequence_viewer_controller.SequenceViewerController`
    (``__len__``, ``__getitem__``, ``find``) while delegating actual data
    retrieval to :meth:`~genetinav.gene_service.GeneService.get_chunked_sequence`.
    """

    def __init__(
        self,
        gene_service,
        species: str,
        chromosome: str,
        base_coord: int,
        total_len: int = 300_000_000,
    ):
        self.gene_service = gene_service
        self.species = species
        self.chromosome = chromosome
        self.base_coord = base_coord
        self.total_len = total_len

    def __len__(self) -> int:
        return self.total_len

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = idx.start or 0
            stop = idx.stop or self.total_len
            abs_start = self.base_coord + start
            abs_stop = self.base_coord + stop - 1
            return self.gene_service.get_chunked_sequence(
                self.species, self.chromosome, abs_start, abs_stop
            )
        return None

    def find(self, sub: str, start: int = 0) -> int:
        search_domain = self.__getitem__(slice(start, start + 10000))
        idx = search_domain.find(sub)
        if idx != -1:
            return start + idx
        return -1


# ── Input modal ──────────────────────────────────────────────────────────────


class _ViewerInputModal(Screen):
    """Minimal inline-prompt modal used for go-to / search."""

    CSS = """
    _ViewerInputModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }
    """

    def __init__(self, prompt_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt_text = prompt_text

    def compose(self) -> ComposeResult:
        with Container(id="viewer-modal-body"):
            yield Label(self.prompt_text, id="viewer-modal-label")
            yield Input(placeholder="", id="viewer-modal-input")

    def on_mount(self) -> None:
        self.query_one("#viewer-modal-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close"),
    ]

    def action_dismiss_modal(self) -> None:
        self.dismiss(None)


# ── Main screen ──────────────────────────────────────────────────────────────


class SequenceViewerScreen(BaseScreen):
    """Professional genomic sequence viewer — palette-driven colours, per-base ruler."""

    # Load styles from dedicated TCSS file
    CSS_PATH = _TCSS_PATH

    BINDINGS = [
        Binding("left",     "move_left",       "◀ 1bp",      show=True),
        Binding("right",    "move_right",       "▶ 1bp",      show=True),
        Binding("up",       "page_backward",    "Page ◀",     show=True),
        Binding("down",     "page_forward",     "Page ▶",     show=True),
        Binding("pageup",   "page_backward",    "Page ◀",     show=False),
        Binding("pagedown", "page_forward",     "Page ▶",     show=False),
        Binding("home",     "jump_to_start",    "⇤ Start",    show=False),
        Binding("end",      "jump_to_end",      "End ⇥",      show=False),
        Binding("g",        "go_to",            "Go to…",     show=True),
        Binding("G",        "go_to",            "Go to…",     show=False),
        Binding("slash",    "search",           "Search",     show=True),
        Binding("n",        "next_match",       "Next",       show=False),
        Binding("N",        "prev_match",       "Prev",       show=False),
        Binding("c",        "toggle_rc",        "Rev-comp",   show=True),
        Binding("C",        "toggle_rc",        "Rev-comp",   show=False),
        Binding("ctrl+g",   "toggle_gc_track",  "GC track",   show=True,  key_display="^g"),
        Binding("ctrl+G",   "toggle_gc_track",  "GC track",   show=False),
        Binding("<",        "history_back",     "← Back",     show=False),
        Binding(">",        "history_forward",  "Fwd →",      show=False),
        Binding("plus",     "zoom_in",          "Zoom in",    show=False),
        Binding("minus",    "zoom_out",         "Zoom out",   show=False),
        Binding("ctrl+p",   "open_palette",     "Commands",   show=False, key_display="^p"),
        Binding("ctrl+P",   "open_palette",     "Commands",   show=False),
        Binding("q",        "quit_viewer",      "Quit",       show=True),
        Binding("Q",        "quit_viewer",      "Quit",       show=False),
        Binding("escape",   "quit_viewer",      "Quit",       show=False),
    ]

    footer_context = "sequence_viewer"

    # ── reactives ────────────────────────────────────────────────────────────

    _window_seq: reactive[str] = reactive("", layout=False)
    _abs_start:  reactive[int] = reactive(0)
    _abs_end:    reactive[int] = reactive(0)
    _matches:    reactive[list] = reactive(list)
    _active_match: reactive[int | None] = reactive(None)
    _match_current: reactive[int] = reactive(0)
    _match_total:   reactive[int] = reactive(0)
    _is_loading:  reactive[bool] = reactive(False)
    _is_error:    reactive[bool] = reactive(False)
    _error_text:  reactive[str]  = reactive("")
    _cached_mb:   reactive[float] = reactive(0.0)
    _reverse_complement: reactive[bool] = reactive(False)
    _show_gc_track:     reactive[bool] = reactive(True)

    def __init__(self, gene_record, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gene_record = gene_record
        self.nav_history = NavigationHistory()

        self.current_species      = gene_record.species
        self.current_chromosome   = gene_record.chromosome
        self.current_base_coord   = gene_record.sequence_window_start
        self.current_gene_symbol  = gene_record.symbol
        self.current_strand       = getattr(gene_record, "strand", "+")
        self.current_offset       = 0

        # Track the genomic boundaries of whichever gene the viewer is
        # currently labelled as.  These are updated whenever boundary detection
        # detects that the viewport has crossed into a different gene.
        self._current_gene_start: int = gene_record.start
        self._current_gene_end:   int = gene_record.end
        # True while we're waiting for the overlap API result to arrive.
        self._gene_label_pending: bool = False

    # ── controller factory ───────────────────────────────────────────────────

    def _make_ctrl(self) -> SequenceViewerController:
        seq_proxy = SequenceProxy(
            gene_service=self.app.gene_service,
            species=self.current_species,
            chromosome=self.current_chromosome,
            base_coord=self.current_base_coord,
            total_len=300_000_000,
        )
        window_size = self.app.settings.get("default_window_size", 60)
        return SequenceViewerController(
            full_sequence=seq_proxy,
            window_start=self.current_offset,
            window_size=window_size,
        )

    # ── compose ──────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield from super().compose()

        self.ctrl = self._make_ctrl()
        self.nav_history.push(
            self.current_chromosome,
            self.current_base_coord + self.ctrl.window_start,
        )

        with Vertical(id="viewer-layout"):
            with Container(id="viewer-card"):
                # ── header row: title + minimap + match counter
                with Horizontal(id="card-header"):
                    yield Label("", id="gene-title")
                    yield MinimapWidget(
                        chromosome=self.current_chromosome,
                        id="minimap",
                    )
                    yield Label("", id="match-counter")

                yield Rule(classes="viewer-rule")

                # ── ruler
                yield RulerWidget(
                    start_coord=self.current_base_coord,
                    window_size=self.app.settings.get("default_window_size", 60),
                    minor_interval=self.app.settings.get("ruler_interval", 10),
                    id="ruler",
                )

                # ── sequence track
                yield SequenceTrackWidget(
                    strand=self.current_strand,
                    id="seq-track",
                )

                # ── GC content track
                yield GcTrackWidget(id="gc-track")

                yield Rule(classes="viewer-rule")

                # ── legend strip (fixed, always visible)
                yield LegendWidget(id="legend-strip")

                yield Rule(classes="viewer-rule")

                # ── stats footer
                yield StatsFooter(id="stats-row")

        # Textual built-in footer for BINDINGS display is inherited from BaseScreen

    def on_mount(self) -> None:
        # Pre-warm the overlap cache for the current gene's region so the
        # first boundary crossing resolves instantly from cache.
        try:
            self.app.gene_service.lookup_gene_at_coords(
                self.current_species,
                self.current_chromosome,
                self._current_gene_start,
                self._current_gene_end,
            )
        except Exception:
            pass
        self._refresh_all()

    # ── state helpers ─────────────────────────────────────────────────────────

    def _state(self) -> dict:
        return {
            "species":    self.current_species,
            "chromosome": self.current_chromosome,
            "base_coord": self.current_base_coord,
            "symbol":     self.current_gene_symbol,
        }

    def _active_palette_colors(self) -> dict:
        """Resolve the current theme's base colours to hex strings."""
        try:
            return get_palette_colors(self.app)
        except Exception:
            from genetinav.ui_textual.widgets import IGV_COLORS
            return dict(IGV_COLORS)

    # ── core update ──────────────────────────────────────────────────────────

    def _refresh_all(self) -> None:
        """Compute all derived state and push to reactive attributes.

        Two-tiered data fetching:
          1. Kick off an async prefetch for the next chunk (gene-level metadata
             is already set from the incoming GeneRecord).
          2. Synchronously resolve the viewport window sequence, then compute
             GC% and base counts from that exact slice.

        If both the prefetch cache and the blocking fetch return no data, we
        set is_error=True and display a clear "Sequence Unavailable" message
        rather than silently defaulting stats to 0 / 0.0%.
        """
        ctrl = self.ctrl
        state = self._state()

        # ── search state ─────────────────────────────────────────────────────
        total_matches = len(ctrl.search_matches)
        active_idx    = None
        match_current = 0
        match_total   = total_matches

        if ctrl.search_query and total_matches > 0:
            raw_idx = next(
                (i for i, m in enumerate(ctrl.search_matches) if m >= ctrl.window_start),
                total_matches,
            )
            active_idx    = raw_idx if raw_idx < total_matches else 0
            match_current = active_idx + 1

        matches_in_window = [
            m - ctrl.window_start
            for m in ctrl.search_matches
            if ctrl.window_start <= m <= ctrl.window_start + ctrl.window_size
        ]
        active_match_in_window: int | None = None
        if active_idx is not None and active_idx < total_matches:
            rel = ctrl.search_matches[active_idx] - ctrl.window_start
            if 0 <= rel <= ctrl.window_size:
                active_match_in_window = rel

        # ── absolute coords ───────────────────────────────────────────────────
        abs_start = state["base_coord"] + ctrl.window_start
        abs_end   = abs_start + ctrl.window_size - 1

        # ── dynamic gene-label detection ──────────────────────────────────────
        # Check whether the viewport has drifted outside the boundaries of the
        # gene we're currently labelled as.  We use a small tolerance (half the
        # window) to avoid flickering right at the border.
        viewport_outside = (
            abs_end   < self._current_gene_start or
            abs_start > self._current_gene_end
        )
        if viewport_outside:
            gene_hit = self.app.gene_service.find_gene_at_pos(
                state["species"],
                state["chromosome"],
                abs_start,
                abs_end,
            )
            if gene_hit is None:
                # Fetch in-flight — keep existing label but mark pending
                self._gene_label_pending = True
            elif gene_hit == {}:
                # Confirmed intergenic region
                self._gene_label_pending = False
                new_symbol = f"intergenic ({state['chromosome']}:{abs_start:,}–{abs_end:,})"
                if new_symbol != state["symbol"]:
                    self.current_gene_symbol = new_symbol
                    state["symbol"] = new_symbol
                    # Reset boundaries to a 500 kbp sentinel so the check fires
                    # again once we leave this intergenic stretch
                    self._current_gene_start = abs_start - 250_000
                    self._current_gene_end   = abs_end   + 250_000
            else:
                # We've entered a new named gene
                new_symbol = gene_hit.get("external_name") or gene_hit.get("id", "unknown")
                self._gene_label_pending = False
                if new_symbol != state["symbol"]:
                    # Push nav history for the boundary crossing
                    self.nav_history.push(
                        state["chromosome"],
                        abs_start,
                    )
                    self.current_gene_symbol    = new_symbol
                    state["symbol"]             = new_symbol
                    self._current_gene_start    = gene_hit.get("start", abs_start)
                    self._current_gene_end      = gene_hit.get("end",   abs_end)
        else:
            # Viewport is back inside the active gene — clear any pending flag
            self._gene_label_pending = False

        # ── two-tiered fetch ──────────────────────────────────────────────────
        # Tier 1: kick off background prefetch (non-blocking)
        self.app.gene_service.prefetch_chunks(
            state["species"], state["chromosome"], abs_start, abs_end
        )

        # Tier 2: resolve the viewport sequence synchronously
        window_seq = ctrl.current_window_sequence()
        is_loading = False
        is_error   = False
        error_text = ""

        if window_seq is None:
            is_loading = True
            window_seq = self.app.gene_service.fetch_chunked_sequence_blocking(
                state["species"], state["chromosome"], abs_start, abs_end
            )
            is_loading = False

        # Check for a background prefetch error regardless of local result
        bg_err = self.app.gene_service.get_prefetch_error(
            state["species"], state["chromosome"]
        )
        if bg_err:
            is_error   = True
            error_text = f"⚠ {str(bg_err)[:60]}"

        # Explicit unavailability: both cache miss and blocking fetch returned nothing
        if window_seq is None or window_seq == "":
            if not is_error:
                is_error   = True
                error_text = _SEQ_UNAVAILABLE
            window_seq = ""

        # ── viewport-level stats (calculated from actual window slice) ────────
        # Only compute real stats when we have real data; keep zeros for error state
        if window_seq and not is_error:
            counts  = base_counts(window_seq)
            gc_pct  = float(gc_percentage(window_seq))
        elif window_seq and is_error:
            # Partial data available despite error — still show real counts
            counts  = base_counts(window_seq)
            gc_pct  = float(gc_percentage(window_seq))
        else:
            counts  = {}
            gc_pct  = 0.0

        cached_mb = self.app.gene_service.get_cached_bytes() / 1_000_000

        # ── resolve active palette colours ────────────────────────────────────
        palette_colors = self._active_palette_colors()

        # ── push to widgets ───────────────────────────────────────────────────
        # Card border title = full genomic coordinate string
        strand_char = "+" if self.current_strand in ("+", "1") else "−"
        coord_str   = f"{state['symbol']} — {state['chromosome']}:{abs_start:,}–{abs_end:,}  ({strand_char})"
        try:
            self.query_one("#viewer-card").border_title = coord_str
        except Exception:
            pass

        # Gene title label (keep for legacy fallback / narrow terminals)
        try:
            self.query_one("#gene-title", Label).update(
                f"[bold]{state['symbol']}[/]  "
                f"[dim]{state['chromosome']}:{abs_start:,}–{abs_end:,}[/]"
            )
        except Exception:
            pass

        # Match counter
        match_str = ""
        if ctrl.search_query:
            if total_matches > 0:
                match_str = f"match {match_current}/{total_matches}"
            else:
                match_str = "no matches"
        try:
            self.query_one("#match-counter", Label).update(match_str)
        except Exception:
            pass

        # Minimap
        try:
            mm = self.query_one("#minimap", MinimapWidget)
            mm.chromosome    = state["chromosome"]
            mm.viewport_start = abs_start
            mm.viewport_end   = abs_end
        except Exception:
            pass

        # Ruler
        try:
            ruler = self.query_one("#ruler", RulerWidget)
            ruler.start_coord    = abs_start
            ruler.window_size    = ctrl.window_size
            ruler.minor_interval = self.app.settings.get("ruler_interval", 10)
        except Exception:
            pass

        # Sequence track
        try:
            st = self.query_one("#seq-track", SequenceTrackWidget)
            st.window_seq         = window_seq
            st.search_query       = ctrl.search_query
            st.matches_in_window  = matches_in_window
            st.active_match       = active_match_in_window
            st.strand             = strand_char
            st.reverse_complement = self._reverse_complement
            st.palette_colors     = palette_colors
        except Exception:
            pass

        # GC track
        try:
            gc_track = self.query_one("#gc-track", GcTrackWidget)
            gc_track.window_seq = window_seq
            gc_track.display    = self._show_gc_track
        except Exception:
            pass

        # Legend strip
        try:
            legend = self.query_one("#legend-strip", LegendWidget)
            legend.palette_colors = palette_colors
        except Exception:
            pass

        # Stats footer
        try:
            sf = self.query_one("#stats-row", StatsFooter)
            sf.window_size    = ctrl.window_size
            sf.cached_mb      = cached_mb
            sf.gc_pct         = gc_pct
            sf.count_a        = counts.get("A", 0)
            sf.count_t        = counts.get("T", 0)
            sf.count_g        = counts.get("G", 0)
            sf.count_c        = counts.get("C", 0)
            sf.search_query   = ctrl.search_query
            sf.match_current  = match_current
            sf.match_total    = match_total
            sf.is_loading     = is_loading
            sf.is_error       = is_error
            sf.status_text    = error_text if is_error else ("Resolving gene…" if self._gene_label_pending else "Ready")
            sf.palette_colors = palette_colors
        except Exception:
            pass

    # ── actions ───────────────────────────────────────────────────────────────

    def action_move_left(self) -> None:
        self.ctrl.move_left()
        self._refresh_all()

    def action_move_right(self) -> None:
        self.ctrl.move_right()
        self._refresh_all()

    def action_page_backward(self) -> None:
        self.ctrl.page_backward()
        self._refresh_all()

    def action_page_forward(self) -> None:
        self.ctrl.page_forward()
        self._refresh_all()

    def action_jump_to_start(self) -> None:
        self.nav_history.push(
            self.current_chromosome,
            self.current_base_coord + self.ctrl.window_start,
        )
        self.ctrl.jump_to_start()
        self._refresh_all()

    def action_jump_to_end(self) -> None:
        self.nav_history.push(
            self.current_chromosome,
            self.current_base_coord + self.ctrl.window_start,
        )
        # Compute the proxy-space offset of the gene's last base.
        # gene_record.end is the true genomic end of the gene (not
        # sequence_window_end, which is only the tiny initial viewport).
        # current_base_coord is the live proxy anchor (sequence_window_start
        # at launch, may differ after a Go-to navigation).
        gene_end_proxy_offset = self.gene_record.end - self.current_base_coord
        target_start = gene_end_proxy_offset - self.ctrl.window_size + 1
        self.ctrl.jump_to_coordinate(max(0, target_start))
        self._refresh_all()

    def action_go_to(self) -> None:
        def _apply(value: str | None) -> None:
            if not value:
                return
            coord_match = re.match(r"^(?:(chr\w+):)?(\d+)(?:-\d+)?$", value)
            if coord_match:
                chrom, coord_str = coord_match.groups()
                coord = int(coord_str)
                if chrom and chrom != self.current_chromosome:
                    self.nav_history.push(
                        self.current_chromosome,
                        self.current_base_coord + self.ctrl.window_start,
                    )
                    self.current_chromosome = chrom
                    self.current_base_coord = coord
                    self.current_gene_symbol = "Custom"
                    self.current_offset = 0
                    self._current_gene_start = coord - 1
                    self._current_gene_end   = coord + 1
                    self.ctrl = self._make_ctrl()
                    self.nav_history.push(
                        self.current_chromosome,
                        self.current_base_coord + self.ctrl.window_start,
                    )
                else:
                    self.nav_history.push(
                        self.current_chromosome,
                        self.current_base_coord + self.ctrl.window_start,
                    )
                    self.ctrl.jump_to_coordinate(coord - self.current_base_coord)
            else:
                try:
                    window_size = self.app.settings.get("default_window_size", 60)
                    new_record = self.app.gene_service.lookup(
                        value,
                        species=self.current_species,
                        window_size=window_size,
                    )
                    self.nav_history.push(
                        self.current_chromosome,
                        self.current_base_coord + self.ctrl.window_start,
                    )
                    self.current_chromosome   = new_record.chromosome
                    self.current_base_coord   = new_record.sequence_window_start
                    self.current_gene_symbol  = new_record.symbol
                    self.current_offset       = 0
                    self._current_gene_start  = new_record.start
                    self._current_gene_end    = new_record.end
                    self.ctrl = self._make_ctrl()
                    self.nav_history.push(
                        self.current_chromosome,
                        self.current_base_coord + self.ctrl.window_start,
                    )
                except Exception:
                    pass
            self._refresh_all()

        self.app.push_screen(
            _ViewerInputModal("Go to coordinate (e.g. chr9:5057799) or gene symbol:"),
            _apply,
        )

    def action_search(self) -> None:
        def _apply(value: str | None) -> None:
            if value:
                self.ctrl.search(value)
                self._refresh_all()

        self.app.push_screen(
            _ViewerInputModal("Search motif (DNA sequence, e.g. ATGC):"),
            _apply,
        )

    def action_next_match(self) -> None:
        self.ctrl.next_match()
        self._refresh_all()

    def action_prev_match(self) -> None:
        self.ctrl.prev_match()
        self._refresh_all()

    def action_toggle_rc(self) -> None:
        """Toggle reverse-complement display in-place."""
        self._reverse_complement = not self._reverse_complement
        self._refresh_all()

    def action_toggle_gc_track(self) -> None:
        """Show / hide the GC content track row."""
        self._show_gc_track = not self._show_gc_track
        try:
            self.query_one("#gc-track", GcTrackWidget).display = self._show_gc_track
        except Exception:
            pass

    def action_zoom_in(self) -> None:
        self.ctrl.increase_window(10)
        self._refresh_all()

    def action_zoom_out(self) -> None:
        self.ctrl.decrease_window(10)
        self._refresh_all()

    def action_history_back(self) -> None:
        prev_loc = self.nav_history.back(
            self.current_chromosome,
            self.current_base_coord + self.ctrl.window_start,
        )
        if prev_loc:
            chrom, pos = prev_loc
            if chrom == self.current_chromosome:
                self.ctrl.jump_to_coordinate(pos - self.current_base_coord)
            else:
                self.current_chromosome  = chrom
                self.current_base_coord  = pos
                self.current_gene_symbol = "History"
                self.current_offset      = 0
                self.ctrl = self._make_ctrl()
        self._refresh_all()

    def action_history_forward(self) -> None:
        next_loc = self.nav_history.forward(
            self.current_chromosome,
            self.current_base_coord + self.ctrl.window_start,
        )
        if next_loc:
            chrom, pos = next_loc
            if chrom == self.current_chromosome:
                self.ctrl.jump_to_coordinate(pos - self.current_base_coord)
            else:
                self.current_chromosome  = chrom
                self.current_base_coord  = pos
                self.current_gene_symbol = "History"
                self.current_offset      = 0
                self.ctrl = self._make_ctrl()
        self._refresh_all()

    def action_open_palette(self) -> None:
        """Push the command palette pre-populated with viewer commands."""
        from genetinav.ui_textual.command_palette import CommandPaletteModal
        self.app.push_screen(
            CommandPaletteModal(viewer_screen=self),
        )

    def action_quit_viewer(self) -> None:
        self.app.pop_screen()

    # ── viewer-specific commands for command palette ───────────────────────────

    def get_viewer_commands(self) -> dict[str, tuple]:
        """Return viewer commands injectable into CommandPaletteModal."""
        return {
            "go_to":         (self.action_go_to,          "Jump to coordinate or gene",   "g"),
            "search":        (self.action_search,          "Search motif",                 "/"),
            "toggle_rc":     (self.action_toggle_rc,       "Toggle reverse complement",    "c"),
            "toggle_gc":     (self.action_toggle_gc_track, "Toggle GC content track", "ctrl+g"),
            "zoom_in":       (self.action_zoom_in,         "Zoom in (+10bp)",              "+"),
            "zoom_out":      (self.action_zoom_out,        "Zoom out (−10bp)",             "-"),
            "jump_to_start": (self.action_jump_to_start,   "Jump to sequence start",    "Home"),
            "jump_to_end":   (self.action_jump_to_end,     "Jump to sequence end",       "End"),
        }
