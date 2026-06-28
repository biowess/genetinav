"""History Modal for GenetiNav."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label, Footer
from textual.containers import Container
from textual.binding import Binding
from textual import work

class HistoryModal(ModalScreen):
    CSS = """
    HistoryModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }
    #history-container {
        width: 60;
        height: auto;
        max-height: 80%;
        border: solid $border;
        background: $panel;
        padding: 1;
    }
    #history-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss"),
        Binding("q", "dismiss", "Dismiss"),
        Binding("Q", "dismiss", "Dismiss"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="history-container"):
            yield Label("History", id="history-title")
            yield ListView(id="history-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        
        history_records = self.app.history_mgr.list()
        for rec in history_records:
            item = ListItem(Label(f"{rec.gene_symbol} ({rec.species})"))
            item.hist_record = rec
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        rec = event.item.hist_record
        self.dismiss()
        self.lookup_gene(rec.gene_symbol, rec.species, rec.window_size)

    @work(exclusive=True)
    async def lookup_gene(self, gene_symbol: str, species: str, window_size: int) -> None:
        try:
            record = self.app.gene_service.lookup(gene_symbol, species=species, window_size=window_size)
            
            from genetinav.ui_textual.result_screen import ResultScreen
            self.app.call_from_thread(self.app.push_screen, ResultScreen(record))
        except Exception as e:
            self.app.call_from_thread(self.notify, str(e), severity="error")
