from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widgets import Select, Switch, Input, Label, Button, Footer
from textual.binding import Binding
from genetinav.settings import load_settings, save_settings
from genetinav.themes import UI_THEMES


def _theme_options() -> list[tuple[str, str]]:
    """Build Select options from all registered palettes."""
    return [(theme.display_name, key) for key, theme in UI_THEMES.items()]


class SettingsModal(ModalScreen):
    CSS = """
    SettingsModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }
    #settings-container {
        width: 60;
        height: auto;
        max-height: 80%;
        border: solid $border;
        background: $panel;
        padding: 0;
    }
    #settings-titlebar {
        height: 3;
        background: $boost;
        border-bottom: solid $border;
        layout: horizontal;
        padding: 0 1;
        align: left middle;
    }
    #settings-title {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
        color: $text;
    }
    #btn-close-modal {
        width: 5;
        min-width: 5;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
        text-style: bold;
    }
    #btn-close-modal:hover {
        color: $error;
        background: $surface;
    }
    #settings-scroll {
        padding: 1;
    }
    .setting-row {
        height: auto;
        min-height: 3;
        margin-bottom: 1;
        layout: horizontal;
    }
    .setting-label {
        width: 1fr;
        content-align: left middle;
    }
    .setting-widget {
        width: 1fr;
    }
    #settings-buttons {
        height: auto;
        min-height: 3;
        padding: 0 1 1 1;
        layout: horizontal;
        align: right middle;
    }
    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("q", "dismiss", "Cancel"),
        Binding("Q", "dismiss", "Cancel"),
        Binding("enter", "save", "Save")
    ]

    def compose(self) -> ComposeResult:
        self.settings_data = load_settings()
        theme_options = _theme_options()
        valid_keys = {v for _, v in theme_options}
        saved_theme = self.settings_data.get("theme", "")
        # Fall back to the first palette key if the saved value isn't in the list
        initial_theme = saved_theme if saved_theme in valid_keys else theme_options[0][1]

        with Container(id="settings-container"):
            with Horizontal(id="settings-titlebar"):
                yield Label("Settings", id="settings-title")
                yield Button("✕", id="btn-close-modal", variant="default")

            with VerticalScroll(id="settings-scroll"):
                with Horizontal(classes="setting-row"):
                    yield Label("Theme", classes="setting-label")
                    yield Select(theme_options, 
                                 value=initial_theme, 
                                 id="setting-theme", classes="setting-widget")

                with Horizontal(classes="setting-row"):
                    yield Label("History Enabled", classes="setting-label")
                    yield Switch(value=self.settings_data.get("history_enabled", True), 
                                 id="setting-history", classes="setting-widget")

                with Horizontal(classes="setting-row"):
                    yield Label("Cache Enabled", classes="setting-label")
                    yield Switch(value=self.settings_data.get("cache_enabled", True), 
                                 id="setting-cache", classes="setting-widget")

                with Horizontal(classes="setting-row"):
                    yield Label("Default Window Size", classes="setting-label")
                    yield Input(value=str(self.settings_data.get("default_window_size", 60)), 
                                id="setting-window-size", classes="setting-widget")

                with Horizontal(classes="setting-row"):
                    yield Label("Default Species", classes="setting-label")
                    yield Input(value=self.settings_data.get("default_species", "human"), 
                                id="setting-species", classes="setting-widget")

            with Horizontal(id="settings-buttons"):
                yield Button("Cancel", id="btn-cancel", variant="error")
                yield Button("Save", id="btn-save", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        theme_select = self.query_one("#setting-theme", Select)
        self.watch(theme_select, "expanded", self._on_theme_expanded)

    def _on_theme_expanded(self, expanded: bool) -> None:
        scroll = self.query_one("#settings-scroll", VerticalScroll)
        scroll.styles.overflow_y = "hidden" if expanded else "auto"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ("btn-cancel", "btn-close-modal"):
            self.dismiss()
        elif event.button.id == "btn-save":
            self.action_save()

    def action_save(self) -> None:
        self.save_all()
        self.dismiss()

    def save_all(self) -> None:
        new_theme = self.query_one("#setting-theme", Select).value
        self.settings_data["theme"] = new_theme
        self.settings_data["history_enabled"] = self.query_one("#setting-history", Switch).value
        self.settings_data["cache_enabled"] = self.query_one("#setting-cache", Switch).value

        try:
            self.settings_data["default_window_size"] = int(
                self.query_one("#setting-window-size", Input).value
            )
        except ValueError:
            pass

        self.settings_data["default_species"] = self.query_one("#setting-species", Input).value

        save_settings(self.settings_data)

        # Propagate settings to the running app
        if hasattr(self.app, "settings"):
            self.app.settings = self.settings_data

        # Live theme switch: swap CSS class and refresh all screens immediately
        if hasattr(self.app, "apply_theme"):
            self.app.apply_theme(new_theme)
