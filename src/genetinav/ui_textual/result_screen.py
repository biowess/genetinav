"""Result Screen for GenetiNav Textual app."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, Markdown
from textual.reactive import reactive

from genetinav.ui_textual.base_screen import BaseScreen
from genetinav.models import GeneRecord

class ResultScreen(BaseScreen):
    CSS = """
    ResultScreen {
        align: center middle;
    }
    #main-layout {
        width: 60;
        height: auto;
        border: solid $panel;
        padding: 1 2;
        background: $surface;
    }
    .header {
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
        width: 100%;
    }
    .metadata-grid {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        height: auto;
        margin-bottom: 1;
    }
    #summary-container {
        border-top: solid $panel;
        padding-top: 1;
        margin-top: 1;
        height: auto;
    }
    """

    BINDINGS = [
        ("o", "open_viewer", "Open viewer"),
        ("O", "open_viewer", "Open viewer"),
        ("v", "toggle_favorite", "Toggle favorite"),
        ("V", "toggle_favorite", "Toggle favorite"),
        ("c", "show_coordinates", "Copy coordinates"),
        ("C", "show_coordinates", "Copy coordinates"),
        ("n", "new_search", "New search"),
        ("N", "new_search", "New search"),
        ("m", "menu", "Menu"),
        ("M", "menu", "Menu"),
        ("q", "back_to_search", "Back"),
        ("Q", "back_to_search", "Back"),
        ("escape", "back_to_search", "Back"),
    ]

    footer_context = "result"
    status_msg = reactive("")

    def __init__(self, gene_record: GeneRecord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gene_record = gene_record

    def compose(self) -> ComposeResult:
        yield from super().compose()
        
        gene = self.gene_record
        seq_len = f"{gene.sequence_window_end - gene.sequence_window_start:,}"

        with Vertical(id="main-layout"):
            yield Label(f"{gene.symbol} - {gene.display_name or 'Unknown'}", classes="header bright")
            
            with Container(classes="metadata-grid"):
                yield Label("Species", classes="dim")
                yield Label(str(gene.species), classes="bright")
                
                yield Label("Chromosome", classes="dim")
                yield Label(str(gene.chromosome), classes="bright")
                
                yield Label("Start", classes="dim")
                yield Label(f"{gene.start:,}", classes="bright")
                
                yield Label("End", classes="dim")
                yield Label(f"{gene.end:,}", classes="bright")
                
                yield Label("Strand", classes="dim")
                yield Label(str(gene.strand), classes="bright")
                
                yield Label("Sequence length", classes="dim")
                yield Label(seq_len, classes="bright")
                
                yield Label("ID", classes="dim")
                yield Label(str(gene.gene_id) if gene.gene_id else "N/A", classes="bright")
                
                yield Label("Assembly", classes="dim")
                yield Label(str(gene.assembly_name) if gene.assembly_name else "N/A", classes="bright")

            if gene.summary:
                with Container(id="summary-container"):
                    yield Label("Summary", classes="dim")
                    yield Markdown(gene.summary)

    async def action_open_viewer(self):
        import asyncio
        from genetinav.ui_textual.loading_screen import LoadingScreen
        from genetinav.ui_textual.sequence_viewer_screen import SequenceViewerScreen
        
        await self.app.push_screen(LoadingScreen("Opening viewer..."))
        start_time = asyncio.get_event_loop().time()
        
        # Pre-fetch the sequence data in the background so the viewer mounts instantly
        record = self.gene_record
        window_size = self.app.settings.get("default_window_size", 60)
        abs_start = record.sequence_window_start
        abs_end = abs_start + window_size - 1
        
        await asyncio.to_thread(
            self.app.gene_service.fetch_chunked_sequence_blocking,
            record.species, record.chromosome, abs_start, abs_end
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)
            
        self.app.pop_screen()
        await self.app.push_screen(SequenceViewerScreen(self.gene_record))

    def action_toggle_favorite(self):
        is_fav = self.app.favorites_mgr.is_favorite(self.gene_record.symbol, self.gene_record.species)
        if is_fav:
            self.app.favorites_mgr.remove(self.gene_record.symbol, self.gene_record.species)
            self.notify(f"Removed {self.gene_record.symbol} from favorites.", severity="information")
        else:
            self.app.favorites_mgr.add(self.gene_record.symbol, self.gene_record.species)
            self.notify(f"Added {self.gene_record.symbol} to favorites.", severity="information")

    def action_show_coordinates(self):
        self.notify(f"{self.gene_record.chromosome}:{self.gene_record.start:,}–{self.gene_record.end:,}", severity="information", title="Coordinates Copied")

    def action_new_search(self):
        self.app.pop_screen()

    def action_back_to_search(self):
        self.app.pop_screen()

    async def action_menu(self):
        from genetinav.ui_textual.menu_modal import MenuModal
        await self.app.push_screen(MenuModal(self.gene_record))
