"""The colors and the fonts of the trailer: the GRADIENT brand of Termina, in its light mode."""

from pathlib import Path

import manimpango

HUESO = "#f6f6f3"    # background
GRAFITO = "#0e1116"  # text and main actions
ACERO = "#5b616b"    # secondary text
NIEBLA = "#d9dbdf"   # lines
AZUL = "#2b59ff"     # only as a signal
HIELO = "#dce4ff"    # the tint of AZUL
OK = "#1f9d55"

# The names that the themes of Termina change.
BACKGROUND = HUESO
TEXT = GRAFITO
SECONDARY = ACERO
ACCENT = AZUL
FONT = "Space Grotesk"

for font in sorted((Path(__file__).parent / "fonts").glob("*.ttf")):
    manimpango.register_font(str(font))

# The themes of Termina (studio.THEMES): background, text, secondary, accent.
THEMES = {
    "dark": ("#1f1e1d", "#faf9f5", "#c2c0b6", "#d97757"),
    "light": (HUESO, GRAFITO, ACERO, AZUL),
    "night": ("#0b1020", "#e8ecff", "#9aa3c7", "#7aa2ff"),
    "paper": ("#fbf7ee", "#2b2620", "#7a7065", "#b4532a"),
}


def palette(theme):
    """The colors that a slide of an example gets in a theme. The examples have a fifth color,
    BLUE, for lines: it takes the color of the text."""
    bg, text, secondary, accent = THEMES[theme]
    return [bg, text, secondary, accent, text]
