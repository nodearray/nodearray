"""Builds tech-stack.svg: the tech-stack icon row as one local image.

Usage:  python make_icons.py

Most tiles come from skillicons.dev (dark theme). Burp Suite is not available
there, so its tile is drawn here in the same style (logo path from Simple Icons, CC0).
"""

import re
import urllib.request
from pathlib import Path

ICONS = ["py", "electron", "nodejs", "supabase", "docker", "burpsuite", "git", "github", "windows"]

TILE, STEP = 256, 300  # same tile size and spacing as skillicons.dev

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


def build_svg():
    width = len(ICONS) * STEP - (STEP - TILE)
    tiles = "\n".join(
        f'  <g transform="translate({i * STEP}, 0)">{fetch_tile(name)}</g>' for i, name in enumerate(ICONS)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * 48 // TILE}" height="48" '
        f'viewBox="0 0 {width} {TILE}" fill="none">\n{tiles}\n</svg>\n'
    )


if __name__ == "__main__":
    target = Path(__file__).with_name("tech-stack.svg")
    target.write_text(build_svg(), encoding="utf-8")
    print(f"{len(ICONS)} icons -> {target}")
