"""UITheme registry for GenetiNav Textual UI.

All colors are stored as hex strings (#rrggbb) — no Rich name translation
required.  This module is the single source of truth for every visual token
used by the TUI: backgrounds, surfaces, hover states, hero accent, and DNA
base colors.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UITheme:
    """A complete hex-based color theme for the GenetiNav TUI."""

    # Internal key (slug, no spaces)
    name: str
    # Human-readable label shown in Settings
    display_name: str

    # ── Structural surfaces ────────────────────────────────────────────────
    bg: str              # Main app background (very dark, near-black)
    sequencer_bg: str    # Sequence viewer — always slightly lighter than bg
    footer_bg: str       # Footer / status bar
    modal_bg: str        # Modal surface — elevated above everything else
    hover: str           # Hover / highlight interaction state

    # ── Identity ───────────────────────────────────────────────────────────
    hero: str            # Hero logo accent — primary identity color per theme

    # ── DNA base colors ────────────────────────────────────────────────────
    base_a: str
    base_t: str
    base_c: str
    base_g: str
    base_n: str = "#555566"   # Ambiguous / unknown base (universal neutral)


# ── Theme registry ─────────────────────────────────────────────────────────

UI_THEMES: dict[str, UITheme] = {
    "obsidian_helix": UITheme(
        name="obsidian_helix",
        display_name="Obsidian Helix",
        bg="#0B0F14",
        sequencer_bg="#0E141B",
        footer_bg="#0A0D12",
        modal_bg="#121923",
        hover="#1B2A3A",
        hero="#7AE0C3",
        base_a="#4FC1FF",
        base_c="#6EE7A8",
        base_t="#FF6B6B",
        base_g="#FFD166",
    ),
    "midnight_genome": UITheme(
        name="midnight_genome",
        display_name="Midnight Genome",
        bg="#070A0F",
        sequencer_bg="#0B1018",
        footer_bg="#06080C",
        modal_bg="#111827",
        hover="#1A2333",
        hero="#A78BFA",
        base_a="#60A5FA",
        base_c="#34D399",
        base_t="#F87171",
        base_g="#FBBF24",
    ),
    "carbon_strand": UITheme(
        name="carbon_strand",
        display_name="Carbon Strand",
        bg="#0A0A0C",
        sequencer_bg="#101114",
        footer_bg="#08090B",
        modal_bg="#16181D",
        hover="#23262E",
        hero="#22D3EE",
        base_a="#38BDF8",
        base_c="#4ADE80",
        base_t="#FB7185",
        base_g="#FACC15",
    ),
    "void_polymer": UITheme(
        name="void_polymer",
        display_name="Void Polymer",
        bg="#05070A",
        sequencer_bg="#0A0D12",
        footer_bg="#04060A",
        modal_bg="#0F141C",
        hover="#19212C",
        hero="#C084FC",
        base_a="#93C5FD",
        base_c="#86EFAC",
        base_t="#FCA5A5",
        base_g="#FDE047",
    ),
    "deep_cell": UITheme(
        name="deep_cell",
        display_name="Deep Cell",
        bg="#0B0E10",
        sequencer_bg="#11161A",
        footer_bg="#090C0F",
        modal_bg="#161C22",
        hover="#222B33",
        hero="#2DD4BF",
        base_a="#67E8F9",
        base_c="#A7F3D0",
        base_t="#FDA4AF",
        base_g="#FDE68A",
    ),
    "nucleic_night": UITheme(
        name="nucleic_night",
        display_name="Nucleic Night",
        bg="#060812",
        sequencer_bg="#0C1020",
        footer_bg="#05060C",
        modal_bg="#121A2B",
        hover="#1B2A44",
        hero="#818CF8",
        base_a="#60A5FA",
        base_c="#34D399",
        base_t="#FB7185",
        base_g="#F59E0B",
    ),
    "graphene_dark": UITheme(
        name="graphene_dark",
        display_name="Graphene Dark",
        bg="#0A0D0F",
        sequencer_bg="#101418",
        footer_bg="#090B0D",
        modal_bg="#151B20",
        hover="#232B33",
        hero="#14B8A6",
        base_a="#38BDF8",
        base_c="#22C55E",
        base_t="#EF4444",
        base_g="#EAB308",
    ),
    "helix_abyss": UITheme(
        name="helix_abyss",
        display_name="Helix Abyss",
        bg="#05080C",
        sequencer_bg="#0B1118",
        footer_bg="#04070A",
        modal_bg="#111A26",
        hover="#1B2A3F",
        hero="#F472B6",
        base_a="#93C5FD",
        base_c="#6EE7B7",
        base_t="#FCA5A5",
        base_g="#FCD34D",
    ),
    "synthetic_strand": UITheme(
        name="synthetic_strand",
        display_name="Synthetic Strand",
        bg="#0A0B10",
        sequencer_bg="#121520",
        footer_bg="#090A0F",
        modal_bg="#1A1F2E",
        hover="#2A3142",
        hero="#7C3AED",
        base_a="#60A5FA",
        base_c="#4ADE80",
        base_t="#F87171",
        base_g="#FBBF24",
    ),
    "black_helix_neon": UITheme(
        name="black_helix_neon",
        display_name="Black Helix Neon",
        bg="#040507",
        sequencer_bg="#0A0C10",
        footer_bg="#030406",
        modal_bg="#10141C",
        hover="#1C2433",
        hero="#00F5D4",
        base_a="#00BBF9",
        base_c="#00F5A0",
        base_t="#FF4D6D",
        base_g="#FFD60A",
    ),
}

DEFAULT_UI_THEME = "obsidian_helix"


def get_ui_theme(name: str) -> UITheme:
    """Return the UITheme for *name*, or raise ValueError."""
    key = name.lower().replace(" ", "_").replace("-", "_")
    theme = UI_THEMES.get(key)
    if theme is None:
        valid = ", ".join(UI_THEMES.keys())
        raise ValueError(f"Unknown UI theme '{name}'. Valid options: {valid}")
    return theme


def list_ui_theme_names() -> list[str]:
    """Return all registered theme keys in order."""
    return list(UI_THEMES.keys())


def list_ui_themes() -> list[UITheme]:
    """Return all registered UITheme objects in order."""
    return list(UI_THEMES.values())
