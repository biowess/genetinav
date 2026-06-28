"""Theme CSS generator for the GenetiNav Textual UI.

Generates a single CSS string containing one `.theme-<name>` rule-set per
registered UITheme.  The generated CSS is injected as ``App.CSS`` in
``textual_app.py`` so every widget automatically inherits the active theme
without any per-widget hardcoding.

Usage::

    from genetinav.ui_textual.theme import THEME_CSS
    class GenetinavTUI(App):
        CSS = THEME_CSS

Theme switching is done by swapping the ``theme-<name>`` CSS class on the
App root — see ``GenetinavTUI.apply_theme()``.
"""

from __future__ import annotations

from genetinav.themes import UI_THEMES, UITheme


def _dim(hex_color: str, factor: float = 0.55) -> str:
    """Return a dimmer version of *hex_color* by multiplying each channel.

    Used to derive subtle border / rule colors from the hero accent without
    requiring a separate token in every theme definition.
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _mix(hex_a: str, hex_b: str, t: float = 0.5) -> str:
    """Linear-interpolate between two hex colors (t=0 → a, t=1 → b)."""
    def _ch(c: str) -> tuple[int, int, int]:
        h = c.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    ar, ag, ab = _ch(hex_a)
    br, bg, bb = _ch(hex_b)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    b = int(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def _slightly_lighter(hex_color: str, amount: int = 18) -> str:
    """Return *hex_color* brightened by *amount* on each channel (clamped)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def _generate_theme_block(theme: UITheme) -> str:
    """Return the full CSS block for one UITheme, scoped to .theme-<name>."""

    n = f"theme-{theme.name}"          # CSS class prefix

    border        = _dim(theme.hero, 0.45)
    border_bright = _dim(theme.hero, 0.75)
    dim_text      = _mix(theme.bg, "#c0c8d8", 0.55)
    text          = "#d0d8e8"
    card_bg       = _slightly_lighter(theme.sequencer_bg, 10)
    panel_bg      = _slightly_lighter(theme.modal_bg, 8)
    rule_color    = _dim(theme.hero, 0.25)

    return f"""\
/* ══ theme: {theme.display_name} ({theme.name}) ══════════════════════════════════ */

/* ── App / Screen root ─────────────────────────────────────────────────── */
.{n} {{
    background: {theme.bg};
}}
.{n} Screen {{
    background: {theme.bg};
}}

/* ── Sequence viewer surfaces ──────────────────────────────────────────── */
.{n} #viewer-layout {{
    background: {theme.bg};
}}
.{n} #viewer-card {{
    background: {theme.sequencer_bg};
    border: solid {border};
    border-title-color: {theme.hero};
}}
.{n} #legend-strip {{
    background: {card_bg};
    color: {dim_text};
}}
.{n} #stats-row {{
    background: {card_bg};
}}
.{n} .viewer-rule {{
    color: {rule_color};
}}

/* ── Gene title label ──────────────────────────────────────────────────── */
.{n} #gene-title {{
    color: {text};
}}

/* ── Footer ────────────────────────────────────────────────────────────── */
.{n} Footer {{
    background: {theme.footer_bg};
    color: {dim_text};
}}
.{n} Footer > FooterKey {{
    background: transparent;
    color: {dim_text};
}}
.{n} Footer > FooterKey:hover {{
    background: {theme.hover};
    color: {text};
}}
.{n} Footer > FooterKey .footer-key--key {{
    color: {theme.hero};
    background: transparent;
    text-style: bold;
}}
.{n} Footer > FooterKey .footer-key--description {{
    color: {dim_text};
}}

/* ── Inputs ────────────────────────────────────────────────────────────── */
.{n} Input {{
    background: {theme.sequencer_bg};
    border: solid {border};
    color: {text};
}}
.{n} Input:focus {{
    border: solid {theme.hero};
}}

/* ── OptionList / autocomplete ─────────────────────────────────────────── */
.{n} OptionList {{
    background: {theme.modal_bg};
    border: solid {border};
    color: {text};
}}
.{n} OptionList > .option-list--option {{
    color: {text};
}}
.{n} OptionList > .option-list--option-highlighted {{
    background: {theme.hover};
    color: {theme.hero};
}}
.{n} OptionList > .option-list--option:hover {{
    background: {theme.hover};
}}

/* ── ListView / ListItem ───────────────────────────────────────────────── */
.{n} ListView {{
    background: {theme.modal_bg};
    border: solid {border};
}}
.{n} ListView > ListItem {{
    background: transparent;
    color: {text};
}}
.{n} ListView > ListItem.--highlight {{
    background: {theme.hover};
    border-left: solid {theme.hero};
}}
.{n} ListView > ListItem:hover {{
    background: {theme.hover};
}}

/* ── Select widget ─────────────────────────────────────────────────────── */
.{n} Select {{
    background: {theme.sequencer_bg};
    border: solid {border};
    color: {text};
}}
.{n} Select:focus {{
    border: solid {theme.hero};
}}
.{n} SelectOverlay {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}
.{n} SelectOverlay > .option-list--option-highlighted {{
    background: {theme.hover};
    color: {theme.hero};
}}

/* ── Switch widget ─────────────────────────────────────────────────────── */
.{n} Switch.-on .switch--slider {{
    color: {theme.hero};
}}

/* ── Buttons ───────────────────────────────────────────────────────────── */
.{n} Button.success {{
    background: {_dim(theme.hero, 0.35)};
    color: {text};
    border: solid {border_bright};
}}
.{n} Button.success:hover {{
    background: {_dim(theme.hero, 0.5)};
}}

/* ── Modal surfaces ────────────────────────────────────────────────────── */
/* Command Palette */
.{n} #palette-container {{
    background: {theme.modal_bg};
    border: solid {border_bright};
    border-title-color: {theme.hero};
}}
.{n} #palette-input {{
    background: {panel_bg};
    border: solid {border};
    color: {text};
}}
.{n} #palette-input:focus {{
    border: solid {theme.hero};
}}
.{n} #palette-hint {{
    color: {dim_text};
}}
.{n} #palette-options {{
    background: {theme.modal_bg};
    border: solid {border};
}}

/* Settings Modal */
.{n} #settings-container {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}
.{n} #settings-titlebar {{
    background: {panel_bg};
    border-bottom: solid {border};
}}
.{n} #settings-title {{
    color: {text};
}}

/* Help Modal */
.{n} #help-container {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}
.{n} #help-titlebar {{
    background: {panel_bg};
    border-bottom: solid {border};
}}
.{n} #help-title {{
    color: {text};
}}
.{n} .help-section-title {{
    color: {theme.hero};
}}
.{n} .help-key {{
    color: {text};
}}
.{n} .help-desc {{
    color: {dim_text};
}}

/* About Modal */
.{n} #about-container {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}
.{n} #about-titlebar {{
    background: {panel_bg};
    border-bottom: solid {border};
}}
.{n} #about-title {{
    color: {text};
}}
.{n} .about-section-title {{
    color: {theme.hero};
}}
.{n} .about-paragraph {{
    color: {dim_text};
}}
.{n} #license-container {{
    background: {_mix(theme.modal_bg, "#000000", 0.3)};
    border: solid {border};
}}
.{n} #license-title {{
    color: {theme.hero};
}}
.{n} #license-body {{
    color: {_mix(dim_text, "#888899", 0.4)};
}}
.{n} #about-tagline {{
    color: {dim_text};
}}
.{n} #about-divider {{
    color: {rule_color};
}}

/* Menu Modal */
.{n} #menu-container {{
    background: {theme.modal_bg};
    border: solid {theme.hero};
}}
.{n} #menu-title {{
    color: {theme.hero};
}}
.{n} #menu-options {{
    background: {theme.modal_bg};
}}

/* Favorites / History Modals */
.{n} #favorites-container,
.{n} #history-container {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}

/* Inline viewer input modal */
.{n} #viewer-modal-body {{
    background: {theme.modal_bg};
    border: solid {border_bright};
}}
.{n} #viewer-modal-label {{
    color: {dim_text};
}}
.{n} #viewer-modal-input {{
    background: {panel_bg};
    border: solid {border};
    color: {text};
}}
.{n} #viewer-modal-input:focus {{
    border: solid {theme.hero};
}}

/* ── Utility classes ────────────────────────────────────────────────────── */
.{n} .dim {{
    color: {dim_text};
}}
.{n} .bright {{
    color: {theme.hero};
    text-style: bold;
}}

/* ── Result screen ─────────────────────────────────────────────────────── */
.{n} #main-layout {{
    background: {theme.sequencer_bg};
    border: solid {border};
}}
.{n} #summary-container {{
    border-top: solid {border};
}}
/* ── Loading Screen ────────────────────────────────────────────────────── */
.{n} LoadingScreen {{
    background: {_dim(theme.bg, 0.8)};
}}
.{n} #loading-container {{
    background: {theme.modal_bg};
    border: solid {theme.hero};
}}
.{n} #loading-message {{
    color: {text};
}}
.{n} LoadingIndicator {{
    color: {theme.hero};
}}
"""


def generate_theme_css() -> str:
    """Generate the full TCSS string for all registered UITheme palettes."""
    blocks = [_generate_theme_block(theme) for theme in UI_THEMES.values()]

    # Global (theme-independent) rules placed last so themes can override
    blocks.append("""\
/* ── global (theme-independent) ────────────────────────────────────────── */
Screen {
    overflow: hidden hidden;
}
""")
    return "\n".join(blocks)


# Module-level constant — imported by textual_app.py as App.CSS
THEME_CSS = generate_theme_css()
