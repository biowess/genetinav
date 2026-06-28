"""Favorites Modal for GenetiNav."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label, Footer
from textual.containers import Container
from textual.binding import Binding
from textual import work

class FavoritesModal(ModalScreen):
    CSS = """
    FavoritesModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }
    #favorites-container {
        width: 60;
        height: auto;
        max-height: 80%;
        border: solid $border;
        background: $panel;
        padding: 1;
    }
    #favorites-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss"),
        Binding("q", "dismiss", "Dismiss"),
        Binding("Q", "dismiss", "Dismiss"),
        Binding("d", "delete", "Delete Favorite"),
        Binding("D", "delete", "Delete Favorite"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="favorites-container"):
            yield Label("Favorites", id="favorites-title")
            yield ListView(id="favorites-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        
        favorites = self.app.favorites_mgr.list()
        for fav in favorites:
            item = ListItem(Label(f"{fav.gene_symbol} ({fav.species})"))
            item.fav_record = fav
            list_view.append(item)

    def action_delete(self) -> None:
        list_view = self.query_one(ListView)
        if list_view.highlighted_child is not None:
            fav = list_view.highlighted_child.fav_record
            self.app.favorites_mgr.remove(fav.gene_symbol, fav.species)
            self.refresh_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        fav = event.item.fav_record
        self.dismiss()
        self.lookup_gene(fav.gene_symbol, fav.species)

    @work(exclusive=True)
    async def lookup_gene(self, gene_symbol: str, species: str) -> None:
        try:
            window_size = self.app.settings.get("default_window_size", 60)
            record = self.app.gene_service.lookup(gene_symbol, species=species, window_size=window_size)
            
            from genetinav.ui_textual.result_screen import ResultScreen
            await self.app.push_screen(ResultScreen(record))
        except Exception as e:
            self.notify(str(e), severity="error")
