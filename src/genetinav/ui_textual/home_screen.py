import asyncio
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, OptionList, ListView, ListItem, Label, Button, Static
from textual import work, on, events
from textual.message import Message

from genetinav.command_parser import parse_command
from genetinav.command_router import CommandRouter


def _create_shadowed_wordmark(primary_style: str, shadow_style: str) -> Text:
    """Render the ASCII block-letter wordmark with a drop-shadow effect."""
    lines = [
        "█▀▀▀ █▀▀▀ █▀▀▄ █▀▀▀ ▀▀█▀▀ ▀█▀ █▀▀▄ █▀▀█ █  █",
        "█ ▀█ █▀▀  █  █ █▀▀    █    █  █  █ █▄▄█ █  █",
        "▀▀▀█ ▀▀▀▀ ▀  ▀ ▀▀▀▀   ▀   ▀▀▀ ▀  ▀ ▀  ▀  ▀▀",
    ]
    result = Text()
    height = len(lines)
    width = max(len(line) for line in lines)
    for y in range(height + 1):
        line_text = Text()
        for x in range(width + 1):
            fg_char = " "
            if y < height and x < len(lines[y]):
                fg_char = lines[y][x]
            bg_char = " "
            if y - 1 >= 0 and x - 1 >= 0 and (y - 1) < height and (x - 1) < len(lines[y - 1]):
                bg_char = lines[y - 1][x - 1]
            if fg_char != " ":
                line_text.append(fg_char, style=primary_style)
            elif bg_char != " ":
                line_text.append("█", style=shadow_style)
            else:
                line_text.append(" ")
        result.append(line_text)
        if y < height:
            result.append("\n")
    return result

class SearchInput(Input):
    class AutocompleteRight(Message):
        pass
    class FocusOptions(Message):
        pass

    def on_key(self, event: events.Key) -> None:
        if event.key == "right" and self.cursor_position == len(self.value):
            self.post_message(self.AutocompleteRight())
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            self.post_message(self.FocusOptions())
            event.prevent_default()
            event.stop()

class SearchOptionList(OptionList):
    class FocusInput(Message):
        pass

    def on_key(self, event: events.Key) -> None:
        if event.key == "up" and self.highlighted == 0:
            self.post_message(self.FocusInput())
            event.prevent_default()
            event.stop()


from genetinav.ui_textual.base_screen import BaseScreen

class HomeScreen(BaseScreen):
    CSS = """
    HomeScreen {
        align: center middle;
    }
    #quit-container {
        dock: top;
        height: auto;
        align: right middle;
        padding-top: 1;
        padding-right: 2;
    }
    #quit-button {
        min-width: 5;
        width: 5;
        height: 1;
        border: none;
        padding: 0;
    }
    #home-layout {
        width: 60;
        height: auto;
    }
    #search-input {
        width: 100%;
        margin-bottom: 1;
    }
    #autocomplete-options {
        width: 100%;
        height: auto;
        max-height: 5;
        display: none;
    }
    #wordmark {
        width: 100%;
        height: auto;
        text-align: center;
        margin-bottom: 2;
    }
    """

    footer_context = "search"
    show_footer = False

    BINDINGS = [
        Binding("slash", "focus_search", "Type / Search"),
        Binding("question_mark", "help", "Help", key_display="?"),
    ]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Horizontal(id="quit-container"):
            yield Button("X", id="quit-button", variant="error")
        with Vertical(id="home-layout"):
            yield Static(id="wordmark")
            yield SearchInput(placeholder="Search gene or type /command...", id="search-input")
            yield SearchOptionList(id="autocomplete-options")

    def on_mount(self) -> None:
        self.query_one("#search-input").focus()
        self.refresh_wordmark()
        self.router = self.app.router

    def refresh_wordmark(self) -> None:
        from genetinav.themes import get_ui_theme, DEFAULT_UI_THEME
        theme_name = self.app.settings.get("theme", DEFAULT_UI_THEME)
        try:
            theme = get_ui_theme(theme_name)
        except ValueError:
            theme = get_ui_theme(DEFAULT_UI_THEME)

        primary_style = theme.hero
        shadow_style = "#222222"
        wordmark_text = _create_shadowed_wordmark(primary_style, shadow_style)

        from rich.align import Align
        self.query_one("#wordmark", Static).update(Align.center(wordmark_text))

    def on_input_changed(self, event: Input.Changed) -> None:
        val = event.value.strip()
        options = self.query_one("#autocomplete-options", OptionList)
        options.clear_options()
        
        if val.startswith("/"):
            # Autocomplete commands
            matches = [cmd for cmd in self.router.registry.keys() if cmd.startswith(val[1:])]
            if matches:
                options.display = True
                for match in matches:
                    options.add_option(f"/{match}")
            else:
                options.display = False
        else:
            options.display = False

    @on(SearchInput.AutocompleteRight)
    def on_autocomplete_right(self) -> None:
        options = self.query_one("#autocomplete-options", SearchOptionList)
        if options.display and options.option_count > 0:
            highlighted = options.highlighted if options.highlighted is not None else 0
            if highlighted < options.option_count:
                opt = options.get_option_at_index(highlighted)
                inp = self.query_one("#search-input", SearchInput)
                inp.value = str(opt.prompt) + " "
                inp.cursor_position = len(inp.value)

    @on(SearchInput.FocusOptions)
    def on_focus_options(self) -> None:
        options = self.query_one("#autocomplete-options", SearchOptionList)
        if options.display and options.option_count > 0:
            options.focus()

    @on(SearchOptionList.FocusInput)
    def on_focus_input(self) -> None:
        self.query_one("#search-input", SearchInput).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        # User picked an option, fill input and focus, do NOT submit
        inp = self.query_one("#search-input", SearchInput)
        inp.value = str(event.option.prompt) + " "
        inp.cursor_position = len(inp.value)
        inp.focus()
        options = self.query_one("#autocomplete-options", SearchOptionList)
        options.display = False

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if not val:
            return
            
        cmd, args, err = parse_command(val, list(self.router.registry.keys()))
        if cmd:
            try:
                self.router.dispatch(cmd)
            except Exception as e:
                # Stub catch for missing screens since they aren't implemented yet
                self.notify(f"Dispatched: /{cmd}", severity="info")
        elif not err:
            # Gene search
            self.lookup_gene(val)
        else:
            self.notify(err, severity="error")

    @work(exclusive=True)
    async def lookup_gene(self, gene_symbol: str) -> None:
        try:
            # We assume window_size and species can be obtained or use defaults
            species = self.app.settings.get("default_species", "human")
            window_size = self.app.settings.get("default_window_size", 60)
            
            from genetinav.ui_textual.loading_screen import LoadingScreen
            await self.app.push_screen(LoadingScreen("Loading the gene..."))
            
            start_time = asyncio.get_event_loop().time()
            record = await asyncio.to_thread(
                self.app.gene_service.lookup, gene_symbol, species=species, window_size=window_size
            )
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
                
            self.app.pop_screen()
            
            from genetinav.ui_textual.result_screen import ResultScreen
            await self.app.push_screen(ResultScreen(record))
        except Exception as e:
            from genetinav.ui_textual.loading_screen import LoadingScreen
            if isinstance(self.app.screen, LoadingScreen):
                self.app.pop_screen()
            self.notify(str(e), severity="error")


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit-button":
            await self.app.action_quit()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_submit(self) -> None:
        self.query_one("#search-input", Input).focus()
