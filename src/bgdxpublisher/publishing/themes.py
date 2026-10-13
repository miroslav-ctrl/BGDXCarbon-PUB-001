"""Built-in document palettes; no user CSS or remote assets."""

THEMES = ("light", "dark")

_PALETTES = {
    "light": ("#ffffff", "#202630", "#1659a5", "#f1f3f5", "#aab4c0"),
    "dark": ("#161b22", "#e6edf3", "#79c0ff", "#242c36", "#8b949e"),
}


def theme_css(theme: str) -> str:
    """Return CSS for an explicit built-in theme or reject an invalid name."""
    if theme not in THEMES:
        raise ValueError("Theme must be light or dark.")
    background, foreground, link, code, border = _PALETTES[theme]
    return (
        f"html{{background:{background};color-scheme:{theme}}}"
        "body{font:18px/1.65 system-ui,sans-serif;max-width:760px;"
        f"margin:48px auto;padding:0 24px;color:{foreground}}}"
        f"h1,h2,h3{{line-height:1.2}}a{{color:{link}}}"
        "pre{overflow:auto;padding:18px;"
        f"background:{code};border-radius:6px}}"
        "code{font-family:monospace}blockquote{"
        f"border-left:3px solid {border};margin-left:0;padding-left:20px}}"
    )
