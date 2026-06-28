"""About modal — app identity, description, and full license text."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widgets import Label, Button, Static, Footer


_LICENSE_TEXT = """\
Custom Source-Available License 1.0

Copyright (c) 2026 BIOWESS

All rights reserved except as expressly permitted below.

1. Permission Granted

You are permitted to:

- View and study the source code.
- Clone and download the repository.
- Run the software locally for personal or educational use.
- Modify the source code for personal learning purposes.
- Share snippets or modified versions for non-commercial educational purposes,
  provided proper credit is clearly given to the original author.

2. Restrictions

You may NOT, without prior written permission from the copyright holder:

- Sell this software or any modified version of it.
- Use this software in a commercial product or service.
- Offer this software as a paid SaaS, hosted platform, or subscription service.
- Rebrand, sublicense, or redistribute this software while claiming it as your own work.
- Remove copyright notices, attribution, or license text.
- Use substantial portions of this software in commercial projects.
- Create commercial derivatives based primarily on this project.

3. Attribution Requirement

Any public use, fork, modification, or redistribution of this project or its
derivatives must include visible credit to the original author.

Example attribution:

"Based on genetinav by BIOWESS"

4. Ownership

The software and all associated intellectual property remain the exclusive
property of the copyright holder.

This license does not transfer ownership of the software or grant any trademark rights.

5. Contributions

Unless explicitly stated otherwise, any contributions submitted to this project
may be incorporated into the project under this same license.

6. Warranty Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR
OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.

7. Acceptance

By cloning, downloading, using, or modifying this software, you agree to the
terms of this license."""


class AboutModal(ModalScreen):
    """A scrollable About screen: hero wordmark, description, and full license."""

    DEFAULT_CSS = """
    AboutModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }

    #about-container {
        width: 72;
        height: 90%;
        border: solid $border;
        background: $panel;
        padding: 0;
    }

    /* ── title bar ── */
    #about-titlebar {
        height: 3;
        background: $boost;
        border-bottom: solid $border;
        layout: horizontal;
        padding: 0 1;
        align: left middle;
    }

    #about-title {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
        color: $text;
    }

    #btn-about-close {
        width: 5;
        min-width: 5;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
        text-style: bold;
    }

    #btn-about-close:hover {
        color: $error;
        background: $surface;
    }

    /* ── scrollable body ── */
    #about-scroll {
        padding: 1 2;
    }

    /* ── hero section ── */
    #about-wordmark {
        width: 100%;
        height: auto;
        text-align: center;
        margin-bottom: 1;
        margin-top: 1;
    }

    #about-tagline {
        width: 100%;
        content-align: center middle;
        text-align: center;
        color: $text-muted;
        text-style: italic;
        margin-bottom: 2;
    }

    /* ── description section ── */
    .about-section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 1;
        width: 100%;
    }

    .about-paragraph {
        width: 100%;
        color: $text;
        margin-bottom: 1;
    }

    /* ── divider ── */
    #about-divider {
        width: 100%;
        height: 1;
        color: $text-muted;
        margin-top: 1;
        margin-bottom: 1;
        content-align: center middle;
        text-align: center;
    }

    /* ── license section ── */
    #license-container {
        width: 100%;
        height: auto;
        border: solid $border;
        background: $surface;
        padding: 1 2;
        margin-top: 1;
        margin-bottom: 2;
    }

    #license-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        width: 100%;
        height: auto;
    }

    #license-body {
        width: 100%;
        height: auto;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_about", "Close"),
        Binding("q", "dismiss_about", "Close"),
        Binding("Q", "dismiss_about", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="about-container"):
            # ── Title bar ──────────────────────────────────────────────
            with Horizontal(id="about-titlebar"):
                yield Label("ⓘ  GenetiNav — About", id="about-title")
                yield Button("✕", id="btn-about-close", variant="default")

            # ── Scrollable body ────────────────────────────────────────
            with VerticalScroll(id="about-scroll"):

                # Hero section
                yield Static(id="about-wordmark")
                yield Label(
                    "Fast, terminal-native genomic exploration.",
                    id="about-tagline",
                )

                # Description
                yield Label("What is GenetiNav?", classes="about-section-title")
                yield Label(
                    "GenetiNav is a terminal-native application for exploring human and "
                    "multi-species genomic sequences. It speaks directly to the Ensembl "
                    "REST API, retrieving live gene records and their raw base-pair "
                    "sequences without requiring a local database or a browser.",
                    classes="about-paragraph",
                )
                yield Label(
                    "At its core, GenetiNav is built around a sequence viewer: a "
                    "scrollable, searchable window into a gene's nucleotide strand. "
                    "You can navigate base by base, leap to arbitrary positions, search "
                    "for motifs, and compare annotated regions — all within a focused "
                    "terminal interface that stays out of your way.",
                    classes="about-paragraph",
                )
                yield Label(
                    "Results are cached locally so repeated lookups are instant. "
                    "A favorites system lets you pin genes for quick return, and a "
                    "history log surfaces your recent searches at a glance. Every "
                    "palette, keybinding, and display preference is exposed through a "
                    "live settings panel — no config file editing required.",
                    classes="about-paragraph",
                )
                yield Label(
                    "GenetiNav is designed to complement bioinformatics workflows "
                    "where speed and keyboard fluency matter. Whether you are studying "
                    "a transcript for the first time or revisiting a familiar locus "
                    "mid-analysis, the interface is fast enough to stay in your flow.",
                    classes="about-paragraph",
                )

                # Divider
                yield Label(
                    "─" * 60,
                    id="about-divider",
                )

                # License — use Container (height:auto) so it never collapses,
                # and Static(markup=False) so square-bracket chars in the text
                # are never mis-parsed as Rich markup tags.
                with Container(id="license-container"):
                    yield Static("License", id="license-title")
                    yield Static(_LICENSE_TEXT, id="license-body", markup=False)

            # ── Footer ────────────────────────────────────────────────
            yield Footer()

    def on_mount(self) -> None:
        self._refresh_wordmark()

    def on_screen_resume(self) -> None:
        self._refresh_wordmark()
        self.query_one("#about-scroll", VerticalScroll).scroll_home(animate=False)

    def _refresh_wordmark(self) -> None:
        """Render the shadowed wordmark using the active palette."""
        try:
            from genetinav.themes import get_ui_theme, DEFAULT_UI_THEME
            from rich.text import Text
            from rich.align import Align

            theme_name = self.app.settings.get("theme", DEFAULT_UI_THEME)
            try:
                theme = get_ui_theme(theme_name)
            except ValueError:
                theme = get_ui_theme(DEFAULT_UI_THEME)

            primary_style = theme.hero
            shadow_style = "#222222"

            # Inline shadowed wordmark renderer
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

            self.query_one("#about-wordmark", Static).update(
                Align.center(result)
            )
        except Exception:
            # Graceful degradation: plain text fallback
            self.query_one("#about-wordmark", Static).update(
                "[bold]GenetiNav[/bold]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-about-close":
            self.dismiss()

    def action_dismiss_about(self) -> None:
        self.dismiss()
