"""MenuModal — a modal menu for the result screen."""

from __future__ import annotations

import json
import webbrowser
from datetime import datetime
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import OptionList, Label
from textual.widgets.option_list import Option

from genetinav.models import GeneRecord
from genetinav.utils.export import format_fasta
from genetinav.ui_textual.loading_screen import LoadingScreen

class MenuModal(ModalScreen):
    CSS = """
    MenuModal {
        align: center middle;
        background: $background 80%;
    }
    #menu-container {
        width: 40;
        height: auto;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }
    #menu-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
        text-align: center;
        width: 100%;
    }
    OptionList {
        background: $surface;
        border: none;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close"),
        Binding("q", "dismiss_modal", "Close"),
        Binding("Q", "dismiss_modal", "Close"),
    ]

    def __init__(self, gene_record: GeneRecord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gene_record = gene_record
        self._menu_state = "main"

    def compose(self) -> ComposeResult:
        with Container(id="menu-container"):
            yield Label("Menu", id="menu-title")
            yield OptionList(id="menu-options")

    def on_mount(self) -> None:
        self._populate_main_menu()

    def _populate_main_menu(self) -> None:
        self._menu_state = "main"
        options = self.query_one("#menu-options", OptionList)
        options.clear_options()
        options.add_option(Option("Export...", id="export"))
        options.add_option(Option("Open in Ensembl", id="ensembl"))

    def _populate_export_menu(self) -> None:
        self._menu_state = "export"
        options = self.query_one("#menu-options", OptionList)
        options.clear_options()
        options.add_option(Option("Markdown", id="export_markdown"))
        options.add_option(Option("FASTA →", id="export_fasta_menu"))
        options.add_option(Option("JSON", id="export_json"))
        options.add_option(Option("← Back", id="back"))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        opt_id = event.option.id

        if self._menu_state == "main":
            if opt_id == "export":
                self._populate_export_menu()
            elif opt_id == "ensembl":
                if self.gene_record.gene_id:
                    url = f"https://www.ensembl.org/id/{self.gene_record.gene_id}"
                else:
                    url = f"https://www.ensembl.org/Multi/Search/Results?q={self.gene_record.symbol}"
                webbrowser.open(url)
                self.dismiss()
        elif self._menu_state == "export":
            if opt_id == "back":
                self._populate_main_menu()
            elif opt_id == "export_markdown":
                self._export_markdown()
                self.dismiss()
            elif opt_id == "export_fasta_menu":
                self._populate_export_fasta_menu()
            elif opt_id == "export_json":
                self._export_json()
                self.dismiss()
        elif self._menu_state == "export_fasta":
            if opt_id == "back_to_export":
                self._populate_export_menu()
            elif opt_id.startswith("export_fasta_"):
                format_type = opt_id.replace("export_fasta_", "")
                self._run_export_fasta(format_type)
                self.dismiss()

    def _populate_export_fasta_menu(self) -> None:
        self._menu_state = "export_fasta"
        options = self.query_one("#menu-options", OptionList)
        options.clear_options()
        options.add_option(Option("Genomic FASTA", id="export_fasta_genomic"))
        options.add_option(Option("Transcript FASTA", id="export_fasta_transcript"))
        options.add_option(Option("CDS FASTA", id="export_fasta_cds"))
        options.add_option(Option("← Back", id="back_to_export"))

    def _export_markdown(self) -> None:
        filename = f"{self.gene_record.symbol}_export.md"
        content = f"# {self.gene_record.symbol}\n\n"
        content += f"**Species:** {self.gene_record.species}\n"
        content += f"**Location:** {self.gene_record.chromosome}:{self.gene_record.start}-{self.gene_record.end}\n"
        if self.gene_record.summary:
            content += f"\n## Summary\n{self.gene_record.summary}\n"
        try:
            with open(filename, "w") as f:
                f.write(content)
            self.app.notify(f"Exported to {filename}", severity="information")
        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")

    def _run_export_fasta(self, format_type: str) -> None:
        self.app.push_screen(LoadingScreen("Exporting FASTA..."))
        self._async_export_fasta(format_type)

    @work(thread=True)
    def _async_export_fasta(self, format_type: str) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.gene_record.symbol}_{format_type}_{timestamp}.fasta"
            
            sequence = None
            header_suffix = ""
            
            if format_type == "genomic":
                header_suffix = f"{self.gene_record.chromosome}:{self.gene_record.start}-{self.gene_record.end} genomic"
                sequence = self.gene_record.sequence
                if not sequence:
                    sequence = self.app.gene_service.fetch_chunked_sequence_blocking(
                        self.gene_record.species,
                        self.gene_record.chromosome,
                        self.gene_record.start,
                        self.gene_record.end
                    )
            else:
                if not self.gene_record.gene_id:
                    raise ValueError("Gene ID is required for transcript/CDS export")
                
                t_id = self.app.gene_service.get_canonical_transcript(self.gene_record.gene_id)
                if not t_id:
                    raise ValueError("No transcripts found for this gene")
                
                header_suffix = f"{t_id} {format_type}"
                
                try:
                    sequence = self.app.gene_service.get_transcript_sequence(t_id, is_cds=(format_type == "cds"))
                except Exception as e:
                    if format_type == "cds":
                        # Fallback to transcript
                        sequence = self.app.gene_service.get_transcript_sequence(t_id, is_cds=False)
                        header_suffix += "\n; WARNING: No CDS found, falling back to transcript"
                    else:
                        raise e

            if not sequence:
                sequence = "SEQUENCE_NOT_LOADED"

            header = f"{self.gene_record.symbol} {header_suffix}"
            content = format_fasta(header, sequence)

            with open(filename, "w") as f:
                f.write(content)
            
            def update_ui():
                self.app.pop_screen()
                self.app.notify(f"Exported to {filename}", severity="information")
                
            self.app.call_from_thread(update_ui)
        except Exception as e:
            def show_error():
                self.app.pop_screen()
                self.app.notify(f"Export failed: {e}", severity="error")
            self.app.call_from_thread(show_error)

    def _export_json(self) -> None:
        filename = f"{self.gene_record.symbol}_export.json"
        try:
            with open(filename, "w") as f:
                json.dump(self.gene_record.to_dict(), f, indent=2)
            self.app.notify(f"Exported to {filename}", severity="information")
        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")

    def action_dismiss_modal(self) -> None:
        self.dismiss()
