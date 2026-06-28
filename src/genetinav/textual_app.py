"""Textual Application for GenetiNav."""

import pathlib
from typing import Optional
from textual.app import App
from textual.binding import Binding

from genetinav.api_client import EnsemblClient
from genetinav.cache import CacheManager
from genetinav.db import get_connection, initialize_schema
from genetinav.favorites import FavoritesManager
from genetinav.gene_service import GeneService
from genetinav.history import HistoryManager
from genetinav.settings import load_settings
from genetinav.ui_textual.theme import THEME_CSS
from genetinav.command_router import CommandRouter


class _DummyLive:
    """No-op live context — satisfies CommandRouter's stop/start protocol."""

    def stop(self) -> None:
        pass

    def start(self) -> None:
        pass


class GenetinavTUI(App):
    CSS = THEME_CSS
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("ctrl+Q", "quit", "Quit", show=False),
        Binding("ctrl+p", "command_palette", "Command Palette", show=False),
        Binding("ctrl+P", "command_palette", "Command Palette", show=False),
        Binding("h", "help", "Help", show=False),
        Binding("H", "help", "Help", show=False),
        Binding("f1", "help", "Help", show=False),
        Binding("ctrl+C", "help_quit", "Quit", show=False),
    ]

    def __init__(
        self,
        settings: Optional[dict] = None,
        db_path: Optional[pathlib.Path] = None,
        initial_query: Optional[str] = None,
        initial_screen: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.settings = settings if settings is not None else load_settings()
        self.db_path = db_path
        self.initial_query = initial_query
        self.initial_screen = initial_screen

    def on_mount(self) -> None:
        # --- Database & managers ---
        self._conn = get_connection(self.db_path)
        initialize_schema(self._conn)
        self.cache_mgr = CacheManager(self._conn)
        self.history_mgr = HistoryManager(self._conn)
        self.favorites_mgr = FavoritesManager(self._conn)

        # --- API client & service ---
        self._api_client = EnsemblClient()
        cache_mgr_or_none = self.cache_mgr if self.settings.get("cache_enabled", True) else None
        history_mgr_or_none = self.history_mgr if self.settings.get("history_enabled", True) else None
        self.gene_service = GeneService(
            api_client=self._api_client,
            cache=cache_mgr_or_none,
            history=history_mgr_or_none,
        )

        theme_name = self.settings.get("theme", "obsidian_helix")
        self.add_class(f"theme-{theme_name}")

        self.command_registry = {
            "settings": (lambda: self.push_screen("settings_modal"), "Settings", "s"),
            "help":     (lambda: self.push_screen("help_modal"),     "Help",     "h"),
            "about":    (lambda: self.push_screen("about_modal"),    "About GenetiNav", "a"),
            "history":  (lambda: self.push_screen("history_modal"),  "History",  "y"),
            "favorites":(lambda: self.push_screen("favorites_modal"),"Favorites","f"),
            "recent":   (lambda: self.push_screen("history_modal"),  "Recent searches", "r"),
            "themes":   (self._action_list_themes,   "List available themes", ""),
            "theme":    (self._prompt_theme_switch,  "Switch theme",          ""),
        }
        self.router = CommandRouter(self.command_registry, _DummyLive())

        from genetinav.ui_textual.settings_modal import SettingsModal
        self.install_screen(SettingsModal(), name="settings_modal")

        from genetinav.ui_textual.history_modal import HistoryModal
        self.install_screen(HistoryModal(), name="history_modal")

        from genetinav.ui_textual.favorites_modal import FavoritesModal
        self.install_screen(FavoritesModal(), name="favorites_modal")

        from genetinav.ui_textual.help_modal import HelpModal
        self.install_screen(HelpModal(), name="help_modal")

        from genetinav.ui_textual.about_modal import AboutModal
        self.install_screen(AboutModal(), name="about_modal")

        from genetinav.ui_textual.home_screen import HomeScreen
        home = HomeScreen()
        self.push_screen(home)

        if self.initial_screen == "settings":
            self.push_screen("settings_modal")
        elif self.initial_query:
            home.lookup_gene(self.initial_query)

    def action_command_palette(self) -> None:
        from genetinav.ui_textual.command_palette import CommandPaletteModal
        self.push_screen(CommandPaletteModal())

    def action_help(self) -> None:
        self.push_screen("help_modal")

    async def action_quit(self) -> None:
        """Exit the application immediately."""
        self.exit()

    def _action_list_themes(self) -> None:
        from genetinav.themes import list_ui_theme_names
        names = ", ".join(list_ui_theme_names())
        self.notify(f"Available themes: {names}", title="Themes", timeout=5)

    def _prompt_theme_switch(self) -> None:
        from genetinav.ui_textual.sequence_viewer_screen import _ViewerInputModal
        from genetinav.themes import list_ui_theme_names

        def _apply(value: str | None) -> None:
            if not value:
                return
            value = value.strip().lower().replace(" ", "_").replace("-", "_")
            if value in list_ui_theme_names():
                self.apply_theme(value)
            else:
                self.notify(f"Unknown theme: {value}", severity="error")

        self.push_screen(_ViewerInputModal("Enter theme name:"), _apply)

    def apply_theme(self, theme_name: str) -> None:
        """Swap the active CSS theme class and repaint all screens.

        Removes any existing ``theme-<old>`` class from the app root, adds
        ``theme-<new>``, updates ``self.settings["theme"]``, and triggers a
        full layout refresh so every mounted screen immediately reflects the
        new palette.
        """
        for cls in list(self.classes):
            if cls.startswith("theme-"):
                self.remove_class(cls)
        self.add_class(f"theme-{theme_name}")
        self.settings["theme"] = theme_name
        from genetinav.settings import save_settings
        save_settings(self.settings)
        self.refresh(layout=True)

        # Refresh wordmark so the logo updates instantly
        for screen in self.screen_stack:
            if hasattr(screen, "refresh_wordmark"):
                try:
                    screen.refresh_wordmark()
                except Exception:
                    pass
