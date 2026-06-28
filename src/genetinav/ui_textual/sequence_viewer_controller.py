"""Sequence viewer navigation and search controller.

Pure logic class — no rendering, no Rich, no Textual imports.
Manages a sliding window over a sequence (string or proxy), and
provides move / page / jump / search methods used by
:class:`~genetinav.ui_textual.sequence_viewer_screen.SequenceViewerScreen`.
"""
from __future__ import annotations

from genetinav.sequence import clamp_window, shift_window


class SequenceViewerController:
    """Stateful sliding-window controller for a DNA sequence."""

    def __init__(
        self,
        full_sequence: str,
        window_start: int = 0,
        window_size: int = 60,
        fine_step: int = 1,
        large_step: int | None = None,
        min_window_size: int = 10,
        max_window_size: int = 5000,
    ):
        self.full_sequence = full_sequence
        self.window_size = min(max(window_size, min_window_size), max_window_size)
        self.fine_step = fine_step
        self.large_step = large_step if large_step is not None else self.window_size
        self.min_window_size = min_window_size
        self.max_window_size = max_window_size

        start, _ = clamp_window(window_start, self.window_size, len(self.full_sequence))
        self.window_start = start

        self.needs_refresh = False

        self.search_query = ""
        self.search_matches: list[int] = []

    # ── coordinate helpers ────────────────────────────────────────────────────

    def jump_to_coordinate(self, coord: int) -> None:
        self.window_start, _ = clamp_window(coord, self.window_size, len(self.full_sequence))

    def jump_to_start(self) -> None:
        self.window_start, _ = clamp_window(0, self.window_size, len(self.full_sequence))

    def jump_to_end(self) -> None:
        self.window_start, _ = clamp_window(
            len(self.full_sequence) - self.window_size,
            self.window_size,
            len(self.full_sequence),
        )

    # ── search ────────────────────────────────────────────────────────────────

    def search(self, query: str, search_domain: str | None = None, domain_offset: int = 0) -> None:
        self.search_query = query.upper()
        self.search_matches = []
        if not query:
            return

        domain = search_domain if search_domain is not None else self.full_sequence

        if isinstance(domain, str):
            idx = domain.find(self.search_query)
            while idx != -1:
                self.search_matches.append(idx + domain_offset)
                idx = domain.find(self.search_query, idx + 1)

    def next_match(self) -> None:
        if not self.search_matches:
            return
        for match in self.search_matches:
            if match > self.window_start:
                self.jump_to_coordinate(match)
                return
        # Wrap around to the first match
        self.jump_to_coordinate(self.search_matches[0])

    def prev_match(self) -> None:
        if not self.search_matches:
            return
        for match in reversed(self.search_matches):
            if match < self.window_start:
                self.jump_to_coordinate(match)
                return
        # Wrap around to the last match
        self.jump_to_coordinate(self.search_matches[-1])

    # ── window property ───────────────────────────────────────────────────────

    @property
    def window_end(self) -> int:
        _, end = clamp_window(self.window_start, self.window_size, len(self.full_sequence))
        return end

    # ── movement ──────────────────────────────────────────────────────────────

    def move_left(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), -self.fine_step
        )

    def move_right(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), self.fine_step
        )

    def page_backward(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), -self.large_step
        )

    def page_forward(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), self.large_step
        )

    def fine_step_backward(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), -1
        )

    def fine_step_forward(self) -> None:
        self.window_start, _ = shift_window(
            self.window_start, self.window_size, len(self.full_sequence), 1
        )

    # ── window resizing ───────────────────────────────────────────────────────

    def increase_window(self, delta: int = 10) -> None:
        self.window_size = min(self.window_size + delta, self.max_window_size)
        self.window_start, _ = clamp_window(
            self.window_start, self.window_size, len(self.full_sequence)
        )

    def decrease_window(self, delta: int = 10) -> None:
        self.window_size = max(self.window_size - delta, self.min_window_size)
        self.window_start, _ = clamp_window(
            self.window_start, self.window_size, len(self.full_sequence)
        )

    # ── sequence access ───────────────────────────────────────────────────────

    def current_window_sequence(self) -> str:
        return self.full_sequence[self.window_start : self.window_end]

    # ── refresh signalling ────────────────────────────────────────────────────

    def mark_refresh_requested(self) -> None:
        self.needs_refresh = True

    def acknowledge_refresh(self) -> None:
        self.needs_refresh = False
