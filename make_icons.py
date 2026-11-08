"""Builds icons/<name>.svg: one local image per tech-stack icon.

Usage:  python make_icons.py
Each icon is its own <img> in the README, so its title shows on hover.
The script prints the matching README HTML at the end.

Most tiles come from skillicons.dev (dark theme). Burp Suite is not available
there, so its tile is drawn here in the same style (logo path from Simple Icons, CC0).
"""

import re
import urllib.request
from pathlib import Path

ICONS = {
    "py": "Python",
    "electron": "Electron",
    "nodejs": "Node.js",
    "supabase": "Supabase",
    "docker": "Docker",
    "burpsuite": "Burp Suite",
    "git": "Git",
    "github": "GitHub",
    "windows": "Windows",
}

BURP_SUITE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
    '<rect width="256" height="256" rx="60" fill="#242938"/>'
    '<g transform="translate(58 58) scale(5.8333)">'
    '<path fill="#FF6633" d="M0 0v24h24V0Zm11.063 3.357h1.874v2.756L10.41 9.2h2.527v3.748h4.579l-4.578 '
    '5.592v2.104h-1.876v-2.758l2.528-3.086h-2.527V11.05h-4.58l4.58-5.592Z"/></g></svg>'
)


def fetch_tile(name):
    if name == "burpsuite":
        return BURP_SUITE
    url = f"https://skillicons.dev/icons?i={name}&theme=dark"
    request = urllib.request.Request(url, headers={"User-Agent": "profile-icons"})
    svg = urllib.request.urlopen(request, timeout=30).read().decode("utf-8")
    inner = re.search(r'<g transform="translate\(0, 0\)">\s*(<svg.*</svg>)\s*</g>', svg, re.S)
    if not inner:
        raise SystemExit(f"Unknown icon on skillicons.dev: {name}")
    return inner.group(1)


def readme_html():
    tags = [
        f'  <img src="./icons/{name}.svg" alt="{label}" title="{label}" height="48">'
        for name, label in ICONS.items()
    ]
    return "<p>\n" + "\n".join(tags) + "\n</p>"


if __name__ == "__main__":
    folder = Path(__file__).with_name("icons")
    folder.mkdir(exist_ok=True)
    for name in ICONS:
        (folder / f"{name}.svg").write_text(fetch_tile(name) + "\n", encoding="utf-8")
    print(f"{len(ICONS)} icons -> {folder}\n")
    print(readme_html())
