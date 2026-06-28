"""Help modal — displays a full keybinding reference with an X close button."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widgets import Label, Button, Footer


_HELP_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Global",
        [
            ("ctrl+q", "Quit the application"),
            ("ctrl+p", "Open command palette"),
            ("?  /  F1", "Show this help page"),
        ],
    ),
    (
        "Home / Search",
        [
            ("Type", "Enter a gene symbol or /command"),
            ("Enter", "Submit search or selected command"),
            ("↑ ↓", "Move through autocomplete / recent list"),
            ("Esc", "Clear input"),
        ],
    ),
    (
        "Result Screen",
        [
            ("o", "Open sequence viewer"),
            ("v", "Toggle favorite"),
            ("c", "Show genomic coordinates"),
            ("n", "New search"),
            ("q / Esc", "Return to home"),
        ],
    ),
    (
        "Sequence Viewer",
        [
            ("← →  /  l r", "Scroll 1 base pair"),
            ("↑ ↓  /  PgUp PgDn", "Scroll one window width"),
            ("Home / End", "Jump to sequence start / end"),
            ("g", "Go to position"),
            ("< >", "Navigate back / forward in history"),
            ("/ ", "Search sequence"),
            ("n / N", "Next / previous match"),
            ("q / Esc", "Close viewer"),
        ],
    ),
    (
        "Favorites & History",
        [
            ("↑ ↓", "Move through list"),
            ("Enter", "Open selected entry"),
            ("d", "Delete entry (favorites only)"),
            ("q / Esc", "Close modal"),
        ],
    ),
    (
        "Settings",
        [
            ("Tab / Shift+Tab", "Cycle between fields"),
            ("Space", "Toggle switches"),
            ("Enter", "Confirm / Save"),
            ("Esc / q", "Cancel without saving"),
        ],
    ),
]


class HelpModal(ModalScreen):
    """A scrollable help/reference modal with an X close button."""

    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }

    #help-container {
        width: 68;
        height: auto;
        max-height: 88%;
        border: solid $border;
        background: $panel;
        padding: 0;
    }

    /* ── title bar ── */
    #help-titlebar {
        height: 3;
        background: $boost;
        border-bottom: solid $border;
        layout: horizontal;
        padding: 0 1;
        align: left middle;
    }

    #help-title {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
        color: $text;
    }

    #btn-close {
        width: 5;
        min-width: 5;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
        text-style: bold;
    }

    #btn-close:hover {
        color: $error;
        background: $surface;
    }

    /* ── scrollable body ── */
    #help-scroll {
        padding: 1 2;
    }

    /* ── section headers ── */
    .help-section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
        width: 100%;
    }

    /* ── key rows ── */
    .help-row {
        height: auto;
        min-height: 1;
        layout: horizontal;
        width: 100%;
    }

    .help-key {
        width: 22;
        color: $text;
        text-style: bold;
        content-align: left middle;
    }

    .help-desc {
        width: 1fr;
        color: $text-muted;
        content-align: left middle;
    }

    /* removed custom footer css */
    """

    BINDINGS = [
        ("escape", "dismiss_help", "Close"),
        ("q", "dismiss_help", "Close"),
        ("Q", "dismiss_help", "Close"),
        ("?", "dismiss_help", "Close"),
        ("f1", "dismiss_help", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-container"):
            # ── Title bar ──────────────────────────────────────────────
            with Horizontal(id="help-titlebar"):
                yield Label("⌘  GenetiNav — Keyboard Reference", id="help-title")
                yield Button("✕", id="btn-close", variant="default")

            # ── Scrollable body ────────────────────────────────────────
            with VerticalScroll(id="help-scroll"):
                for section_title, bindings in _HELP_SECTIONS:
                    yield Label(f"  {section_title}", classes="help-section-title")
                    for key, description in bindings:
                        with Horizontal(classes="help-row"):
                            yield Label(key, classes="help-key")
                            yield Label(description, classes="help-desc")

            # ── Footer ────────────────────────────────────────────
            yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()

    def action_dismiss_help(self) -> None:
        self.dismiss()
