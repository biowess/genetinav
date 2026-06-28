"""CommandPaletteModal — fuzzy-filterable command palette.

When pushed from SequenceViewerScreen (viewer_screen kwarg provided), the
palette is pre-populated with viewer-specific commands in addition to the
global app registry.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Vertical, Container
from textual.widgets import Input, OptionList, Label, Footer
from textual.widgets.option_list import Option
from textual import events


class CommandPaletteModal(ModalScreen):
    CSS = """
    CommandPaletteModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }
    #palette-container {
        width: 64;
        height: auto;
        max-height: 24;
        border-title-style: bold;
        padding: 1;
    }
    #palette-input {
        width: 100%;
        margin-bottom: 1;
    }
    #palette-hint {
        margin-bottom: 1;
        height: 1;
    }
    #palette-options {
        width: 100%;
    }
    """

    def __init__(self, viewer_screen=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._viewer_screen = viewer_screen
        self._commands: dict[str, tuple] = {}

    # ── compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Container(id="palette-container"):
            yield Label("Type to filter commands  ·  Enter to run  ·  Esc to close", id="palette-hint")
            yield Input(placeholder="▸ command…", id="palette-input")
            yield OptionList(id="palette-options")
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.query_one("#palette-container").border_title = "⌘ Command Palette"
        except Exception:
            pass

        # Build command registry: global app commands + viewer commands
        self._commands = {}

        global_registry = getattr(self.app, "command_registry", {})
        for cmd, info in global_registry.items():
            # info = (handler, description, keybinding)
            desc = info[1] if len(info) > 1 else cmd
            key  = info[2] if len(info) > 2 else ""
            self._commands[f"app:{cmd}"] = (info[0], desc, key)

        if self._viewer_screen is not None:
            viewer_cmds = self._viewer_screen.get_viewer_commands()
            for cmd, info in viewer_cmds.items():
                handler, desc, key = info
                self._commands[f"viewer:{cmd}"] = (handler, desc, key)

        self.query_one("#palette-input", Input).focus()
        self._populate_options("")

    # ── filtering ─────────────────────────────────────────────────────────────

    def _populate_options(self, filter_text: str) -> None:
        options = self.query_one("#palette-options", OptionList)
        options.clear_options()
        ftext = filter_text.lower()

        for cmd_id, (handler, desc, key) in self._commands.items():
            # Fuzzy: filter matches any part of id or description
            if ftext in cmd_id.lower() or ftext in desc.lower():
                # Use rich.text.Text to prevent interpretation of brackets as markup tags
                from rich.text import Text
                label_text = Text(desc)
                if key:
                    label_text = Text(f"{desc}  [{key}]")
                options.add_option(Option(label_text, id=cmd_id))

    # ── events ────────────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        self._populate_options(event.value.strip())

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        cmd_id = event.option.id
        self.dismiss()
        if cmd_id and cmd_id in self._commands:
            handler = self._commands[cmd_id][0]
            try:
                handler()
            except Exception:
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        options = self.query_one("#palette-options", OptionList)
        highlighted = options.highlighted
        if highlighted is not None:
            try:
                opt = options.get_option_at_index(highlighted)
                cmd_id = opt.id
                self.dismiss()
                if cmd_id and cmd_id in self._commands:
                    handler = self._commands[cmd_id][0]
                    handler()
            except Exception:
                self.dismiss()
        else:
            self.dismiss()

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close"),
    ]

    def action_dismiss_modal(self) -> None:
        self.dismiss()
