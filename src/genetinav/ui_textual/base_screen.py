"""Base screen for Textual app providing a common footer."""

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Footer

class BaseScreen(Screen):
    """Base screen that includes a common Textual Footer at the bottom."""
    
    footer_context: str = "any"
    show_footer: bool = True

    def compose(self) -> ComposeResult:
        """Yield the persistent footer if show_footer is True."""
        if self.show_footer:
            yield Footer()
