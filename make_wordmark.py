"""Builds wordmark.svg: an animated terminal window with an ASCII wordmark.

Usage:  python make_wordmark.py
The SVG is embedded in the README as an <img>. GitHub plays the CSS
animations inside it right on the profile (no JavaScript needed).
"""

from pathlib import Path

NAME = "NODEARRAY"
BENUTZER = "nodearray"
BEFEHL = "./wordmark.sh --name"

# 7 Zeilen hohe Blockschrift, "#" = gefüllt
SCHRIFT = {
    "N": ["##....##", "###...##", "####..##", "##.##.##", "##..####", "##...###", "##....##"],
    "O": [".######.", "##....##", "##....##", "##....##", "##....##", "##....##", ".######."],
    "D": ["#######.", "##....##", "##....##", "##....##", "##....##", "##....##", "#######."],
    "E": ["########", "##......", "##......", "######..", "##......", "##......", "########"],
    "A": ["..####..", ".##..##.", "##....##", "##....##", "########", "##....##", "##....##"],
    "R": ["#######.", "##....##", "##....##", "#######.", "##..##..", "##...##.", "##....##"],
    "Y": ["##....##", "##....##", ".##..##.", "..####..", "...##...", "...##...", "...##..."],
}
ABSTAND = 2


def baue_raster(text):
    hoehe = len(SCHRIFT["N"])
    zeilen = ["" for _ in range(hoehe)]
    for i, buchstabe in enumerate(text):
        for z in range(hoehe):
            zeilen[z] += SCHRIFT[buchstabe][z] + ("." * ABSTAND if i < len(text) - 1 else "")
    # Platz für den Schatten rechts und unten
    breite = len(zeilen[0]) + 1
    zeilen = [z + "." for z in zeilen] + ["." * breite]
    return zeilen


def gefuellt(raster, z, s):
    return 0 <= z < len(raster) and 0 <= s < len(raster[0]) and raster[z][s] == "#"


def zu_ascii(raster):
    """Gefüllte Zellen werden zu $/S, der Schatten unten rechts zu +/-."""
    vorne, schatten = [], []
    for z in range(len(raster)):
        v, sch = "", ""
        for s in range(len(raster[0])):
            if gefuellt(raster, z, s):
                innen = all(gefuellt(raster, z + dz, s + ds) for dz, ds in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                v += "$" if innen or (z + s) % 3 else "S"
                sch += " "
            elif gefuellt(raster, z - 1, s - 1):
                v += " "
                sch += "+" if gefuellt(raster, z - 1, s) or gefuellt(raster, z, s - 1) else "-"
            else:
                v += " "
                sch += " "
        vorne.append(v)
        schatten.append(sch)
    return vorne, schatten


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def baue_svg():
    vorne, schatten = zu_ascii(baue_raster(NAME))
    spalten = len(vorne[0])
    zw = 8.4  # Zeichenbreite
    zh = 15   # Zeilenhöhe
    rand = 32
    kunst_x = rand
    kunst_y = 96
    kunst_b = spalten * zw
    breite = int(kunst_b + 2 * rand)
    hoehe = int(kunst_y + len(vorne) * zh + 70)
    prompt = f"{BENUTZER}@github:~$ "
    befehl_x = rand + len(prompt) * zw
    befehl_b = len(BEFEHL) * zw
    zweite_y = kunst_y + len(vorne) * zh + 22

    def textzeile(inhalt, y, klasse):
        return (f'<text x="{kunst_x}" y="{y}" class="{klasse}" textLength="{kunst_b:.1f}" '
                f'lengthAdjust="spacing" xml:space="preserve">{esc(inhalt)}</text>')

    zeilen_svg = []
    for i, (v, sch) in enumerate(zip(vorne, schatten)):
        y = kunst_y + i * zh
        if sch.strip():
            zeilen_svg.append(textzeile(sch, y, "schatten"))
        if v.strip():
            zeilen_svg.append(textzeile(v, y, "vorne"))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{breite}" height="{hoehe}" viewBox="0 0 {breite} {hoehe}" role="img" aria-label="{NAME}">
  <title>{NAME}</title>
  <defs>
    <linearGradient id="verlauf" x1="0" y1="0" x2="{kunst_b:.0f}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#5eead4"/>
      <stop offset="0.5" stop-color="#60a5fa"/>
      <stop offset="1" stop-color="#c084fc"/>
    </linearGradient>
    <linearGradient id="glanz" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#fff" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="befehl-clip"><rect class="tippen" x="{befehl_x:.1f}" y="40" width="{befehl_b:.1f}" height="24"/></clipPath>
    <clipPath id="kunst-clip"><rect class="drucken" x="{kunst_x}" y="{kunst_y - 14}" width="{kunst_b:.1f}" height="{len(vorne) * zh + 6}"/></clipPath>
    <mask id="glanz-maske"><g fill="#fff">{''.join(z.replace('class="vorne"', '') for z in zeilen_svg if 'class="vorne"' in z)}</g></mask>
  </defs>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 13px; }}
    .titel {{ fill: #8b949e; font-size: 12px; }}
    .prompt {{ fill: #7ee787; }}
    .pfad {{ fill: #79c0ff; }}
    .cmd {{ fill: #e6edf3; }}
    .vorne {{ fill: url(#verlauf); font-weight: 700; }}
    .schatten {{ fill: #3b4b6b; }}
    .tippen {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0);
      animation: tippen 1.1s steps({len(BEFEHL)}) 0.5s forwards; }}
    .drucken {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0);
      animation: tippen 1.4s steps({spalten // 2}) 1.9s forwards; }}
    @keyframes tippen {{ to {{ transform: scaleX(1); }} }}
    .cursor1 {{ animation: blinken 1s step-end 0s 2, weg 0s 1.6s forwards; }}
    .cursor2 {{ opacity: 0; animation: an 0s 3.5s forwards, blinken 1s step-end 3.5s infinite; }}
    .zeile2 {{ opacity: 0; animation: an 0s 3.5s forwards; }}
    @keyframes blinken {{ 50% {{ opacity: 0; }} }}
    @keyframes weg {{ to {{ opacity: 0; }} }}
    @keyframes an {{ to {{ opacity: 1; }} }}
    .glanz {{ animation: glanz 4s ease-in-out 3.6s infinite; transform: translateX(-200px); }}
    @keyframes glanz {{ 0% {{ transform: translateX(-200px); }} 60%, 100% {{ transform: translateX({kunst_b + 200:.0f}px); }} }}
  </style>

  <!-- Fenster -->
  <rect x="0.5" y="0.5" width="{breite - 1}" height="{hoehe - 1}" rx="12" fill="#0d1117" stroke="#30363d"/>
  <path d="M0.5 12.5a12 12 0 0 1 12-12h{breite - 25}a12 12 0 0 1 12 12v19h-{breite - 1}z" fill="#161b22"/>
  <line x1="0.5" y1="31.5" x2="{breite - 0.5}" y2="31.5" stroke="#30363d"/>
  <circle cx="20" cy="16" r="6" fill="#ff5f57"/>
  <circle cx="40" cy="16" r="6" fill="#febc2e"/>
  <circle cx="60" cy="16" r="6" fill="#28c840"/>
  <text x="{breite / 2:.0f}" y="20" text-anchor="middle" class="titel">{BENUTZER}@github: ~ — zsh</text>

  <!-- Zeile 1: Befehl wird getippt -->
  <text x="{rand}" y="58" textLength="{len(prompt) * zw:.1f}" lengthAdjust="spacing" xml:space="preserve"><tspan class="prompt">{BENUTZER}@github</tspan><tspan class="cmd">:</tspan><tspan class="pfad">~</tspan><tspan class="cmd">$ </tspan></text>
  <g clip-path="url(#befehl-clip)"><text x="{befehl_x:.1f}" y="58" class="cmd" textLength="{befehl_b:.1f}" lengthAdjust="spacing" xml:space="preserve">{esc(BEFEHL)}</text></g>
  <rect class="cursor1" x="{befehl_x:.1f}" y="46" width="8" height="15" fill="#e6edf3"/>

  <!-- Schriftzug wird ausgegeben -->
  <g clip-path="url(#kunst-clip)">
    {chr(10).join('    ' + z for z in zeilen_svg).strip()}
    <g mask="url(#glanz-maske)"><rect class="glanz" x="{kunst_x - 100}" y="{kunst_y - 14}" width="120" height="{len(vorne) * zh + 6}" fill="url(#glanz)"/></g>
  </g>

  <!-- Zeile 2: neuer Prompt mit blinkendem Cursor -->
  <text x="{rand}" y="{zweite_y}" class="zeile2" textLength="{len(prompt) * zw:.1f}" lengthAdjust="spacing" xml:space="preserve"><tspan class="prompt">{BENUTZER}@github</tspan><tspan class="cmd">:</tspan><tspan class="pfad">~</tspan><tspan class="cmd">$ </tspan></text>
  <rect class="cursor2" x="{befehl_x:.1f}" y="{zweite_y - 12}" width="8" height="15" fill="#e6edf3"/>
</svg>
'''


if __name__ == "__main__":
    ziel = Path(__file__).with_name("wordmark.svg")
    ziel.write_text(baue_svg(), encoding="utf-8")
    vorne, schatten = zu_ascii(baue_raster(NAME))
    for v, s in zip(vorne, schatten):
        print("".join(a if a != " " else b for a, b in zip(v, s)))
    print(f"\nGeschrieben: {ziel}")
