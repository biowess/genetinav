"""Loading Screen for GenetiNav Textual app."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import LoadingIndicator, Label

class LoadingScreen(Screen):
    """A beautiful animated loading screen."""

    CSS = """
    LoadingScreen {
        align: center middle;
    }
    #loading-container {
        width: auto;
        height: auto;
        align: center middle;
        padding: 2 4;
    }
    #loading-message {
        text-style: bold;
        margin-top: 1;
        content-align: center middle;
    }

    """

    def __init__(self, message: str = "Loading...", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="loading-container"):
            yield LoadingIndicator()
            yield Label(self.message, id="loading-message")
