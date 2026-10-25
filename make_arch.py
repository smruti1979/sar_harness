"""Generate the SAR Agent Harness reference architecture diagram (SVG + PNG)."""
import cairosvg

W, H = 1600, 1580
FONT = "Arial, 'Liberation Sans', Helvetica, sans-serif"
NAVY, INK, MUTED = "#1e3a8a", "#0f172a", "#475569"
out = []
add = out.append

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;")

def text(x, y, s, size=16, weight="normal", fill=INK, anchor="start", style=""):
    add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}" {style}>{esc(s)}</text>')

def rect(x, y, w, h, fill, stroke, sw=1.5, r=12, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw}"{d}/>')

def badge(x, y, n):
    add(f'<circle cx="{x}" cy="{y}" r="17" fill="{NAVY}"/>')
    text(x, y + 6, str(n), 18, "bold", "white", "middle")

def panel(y, h, n, title, sub, fill, stroke, tag=None):
    rect(60, y, 1480, h, fill, stroke, 2, 16)
    badge(100, y + 36, n)
    text(130, y + 42, title, 21, "bold", INK)
    tw = len(title) * 14.6
    text(130 + tw + 14, y + 42, sub, 16, "normal", MUTED)
    if tag:
        tx, tw2 = 1540 - 40 - 150, 150
        rect(tx, y + 18, tw2, 30, "white", NAVY, 1.5, 15)
        text(tx + tw2 / 2, y + 39, tag, 14, "bold", NAVY, "middle")

def chips(y, labels, total_w=1340, gap=16, h=46, fill="white", stroke="#3b82f6", special=None):
    n = len(labels)
    w = (total_w - gap * (n - 1)) / n
    x0 = 60 + (1480 - total_w) / 2
    for i, lab in enumerate(labels):
        x = x0 + i * (w + gap)
        if special and i in special:
            rect(x, y, w, h, "#fee2e2", "#dc2626", 1.8, 10, "6 4")
            text(x + w / 2, y + 20, lab, 16, "bold", "#991b1b", "middle")
            text(x + w / 2, y + 38, "untrusted text", 12.5, "normal", "#991b1b", "middle")
        else:
            rect(x, y, w, h, fill, stroke, 1.5, 10)
            text(x + w / 2, y + h / 2 + 6, lab, 16, "normal", INK, "middle")

def arrow(x, y1, y2, color=NAVY):
    add(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" stroke-width="2.6" '
        f'marker-end="url(#ah)"/>')

def pair(y1, y2, down_label, up_label, xd=720, xu=880):
    arrow(xd, y1, y2)
    arrow(xu, y2, y1)
    text(xd - 14, (y1 + y2) / 2 + 5, down_label, 15, "normal", MUTED, "end")
    text(xu + 14, (y1 + y2) / 2 + 5, up_label, 15, "normal", MUTED, "start")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="{FONT}">')
add('<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{NAVY}"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="white"/>')

# ---- title
text(W / 2, 62, "SAR Agent Harness: Reference Architecture", 36, "bold", INK, "middle")
text(W / 2, 98, "Decision support for search and rescue. The model proposes. The harness checks. Humans decide.",
     18, "normal", MUTED, "middle")

# ---- 1 signals
panel(130, 124, 1, "SIGNALS", "what comes in", "#f1f5f9", "#94a3b8")
chips(186, ["Beacon alerts", "Registry", "Weather", "Terrain", "Tips and 911", "Drone / sensor feeds",
            "Incident log"], special={4}, stroke="#94a3b8")
arrow(800, 254, 306)
text(814, 286, "raw signals", 15, "normal", MUTED)

# ---- 2 ingestion
panel(306, 124, 2, "INGESTION AND TRUST", "every record gets a source, a time and a trust level",
      "#eff6ff", "#3b82f6")
chips(362, ["Schema validation", "Timestamps", "Provenance tags", "Stale-data flags", "Injection screening"])
arrow(800, 430, 482)
text(814, 462, "validated, tagged records", 15, "normal", MUTED)

# ---- 3 engine
panel(482, 124, 3, "DETERMINISTIC SEARCH ENGINE", "the math lives here, testable and repeatable",
      "#dbeafe", "#1d4ed8", tag="NO LLM")
chips(538, ["Prior maps", "Bayesian updates", "POA / POD / POS", "Travel-time estimates"],
      stroke="#1d4ed8")
pair(606, 666, "map, POS, verified results", "tool calls")

# ---- 4 harness
rect(60, 666, 1480, 500, "#f8fafc", NAVY, 3, 16)
badge(100, 702, 4)
text(130, 708, "AGENT HARNESS", 21, "bold", INK)
text(130 + 13 * 14.6 + 14, 708, "ordinary code around the model", 16, "normal", MUTED)

# LLM box
rect(400, 736, 800, 104, "#fef3c7", "#d97706", 2.5, 14)
text(800, 774, "LLM: proposes only, never decides", 20, "bold", "#78350f", "middle")
text(800, 806, "Reads messy text  ·  coordinates tools  ·  explains its reasoning", 16, "normal", "#78350f", "middle")
pair(840, 890, "proposals (JSON)", "verified results")
add(f'<line x1="220" y1="890" x2="1380" y2="890" stroke="{NAVY}" stroke-width="2.6"/>')
for i in range(5):
    cx = 85 + i * 290 + 135
    add(f'<line x1="{cx}" y1="890" x2="{cx}" y2="906" stroke="{NAVY}" stroke-width="2.6"/>')

# five components
bx, bw, gap, by, bh = 85, 270, 20, 906, 220
comps = [
    ("Loop", ["Ask, Check, Run, Return", "Hard step limit", "Ends on a verified answer", "Step limit: hand to a human"]),
    ("Tools", ["Read-only: alerts, weather", "Computation: engine calls", "Proposal: draft plans", "Consequential: needs approval"]),
    ("Context", ["Mission, rules, tool docs", "Protocols load on demand", "Tool output is data only", "Never treated as orders"]),
    ("Memory", ["Append-only incident log", "New session replays the log", "Model forgets between shifts", "The files remember"]),
    ("Control (policy engine)", ["Claim verification", "POS stopping rule", "Repeat guard, bounds check", "Error capture, escalation"]),
]
for i, (t, lines) in enumerate(comps):
    x = bx + i * (bw + gap)
    ctrl = i == 4
    rect(x, by, bw, bh, NAVY if ctrl else "white", NAVY, 2, 12)
    fg = "white" if ctrl else INK
    text(x + bw / 2, by + 36, t, 19, "bold", fg, "middle")
    add(f'<line x1="{x+24}" y1="{by+50}" x2="{x+bw-24}" y2="{by+50}" stroke="{"#93c5fd" if ctrl else "#cbd5e1"}" stroke-width="1.5"/>')
    for j, ln in enumerate(lines):
        text(x + 22, by + 82 + j * 32, ("• " if True else "") + ln, 15, "normal", fg)

arrow(800, 1166, 1220)  # placeholder replaced below by pair
out.pop()
pair(1166, 1226, "proposals + evidence", "approve · deny · stop")

# ---- 5 human
panel(1226, 124, 5, "HUMAN COMMAND LAYER", "humans keep every consequential decision", "#dcfce7", "#16a34a")
chips(1282, ["Commander approves or denies", "Dispatch and comms systems", "Audit trail", "Dashboards"],
      stroke="#16a34a")

# ---- deployment strip
text(60, 1392, "DEPLOYMENT OPTIONS", 14, "bold", MUTED)
dw, dg = 480, 20
dep = [("Regional cloud or EOC", "Easiest to run, strongest models. Weak when the network fails."),
       ("Field kit (edge)", "Engine, cached maps and log run locally. LLM optional."),
       ("Hybrid (recommended)", "Engine runs everywhere. LLM is a best-effort layer.")]
for i, (t, d) in enumerate(dep):
    x = 60 + i * (dw + dg)
    rect(x, 1404, dw, 70, "#f8fafc", "#cbd5e1", 1.5, 10)
    text(x + 18, 1432, t, 16, "bold", INK)
    text(x + 18, 1456, d, 13.5, "normal", MUTED)

# ---- legend
ly = 1512
items = [("#dbeafe", "#1d4ed8", "", "Deterministic code"), ("#fef3c7", "#d97706", "", "LLM (proposes only)"),
         ("#dcfce7", "#16a34a", "", "Human"), ("#fee2e2", "#dc2626", "6 4", "Untrusted input")]
x = 60
for f, s, d, lab in items:
    rect(x, ly - 14, 26, 18, f, s, 1.8, 4, d)
    text(x + 36, ly, lab, 14, "normal", MUTED)
    x += 36 + len(lab) * 8.6 + 44
text(60, ly + 34, "Reference design. Controls tested in an 8×8 simulation only. Triage and shift handoff are not yet tested.",
     14, "normal", MUTED, "start")

add("</svg>")
svg = "\n".join(out)
open("/mnt/user-data/outputs/sar_architecture.svg", "w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(), write_to="/mnt/user-data/outputs/sar_architecture.png", scale=2)
print("done")
