#!/usr/bin/env python3
"""Measure a paper figure (.svg / .html / Claude Design .dc.html) at its PRINTED size.

Checks
  ERROR  printed text smaller than the venue minimum (--min-pt) at the placement width
  ERROR  (--max-pt N) printed text larger than N pt, e.g. Nature 7; single letters up to N+1.5 pass (panel labels)
  ERROR  text spilling out of its box (nearest ancestor with a border or fill)
  ERROR  two text runs overlapping
  ERROR  text outside the canvas
  WARN   text hugging its box edge (whole line within 6 px of the border)
  WARN   text crossing a connector line/path (SVG line, polyline, path with no fill)
  WARN   glyphs that silently fall back to another font in PDF export (check marks, stars, arrows)
  WARN   text on a grey background (ICML: text should not appear on a grey background)
  WARN   line / border thinner than --min-line-pt (default 0.5 pt, ICML) at print size
  WARN   boxes in a row or column that are almost but not exactly aligned (off by 0.5-6 px)
  ERROR  (--compare OLD) a label of the original figure is missing in the new one
         = a module, arrow/data name, boundary or decision disappeared or was renamed
  --cvd PREFIX  also writes PREFIX_gray.png, PREFIX_deutan.png, PREFIX_protan.png to check
                that colour is never the only cue (ACL) -- look at them

usage:  python3 figure_audit.py FIG --venue icml [--column] [--png out.png] [--compare OLD] [--cvd PREFIX]
        python3 figure_audit.py FIG --placed-mm 165 --min-pt 8 [--max-pt 12] [--min-line-pt 0.5]   # no preset
        --venue   preset for the printed width and the limits: icml neurips iclr acl (emnlp naacl eacl aacl) aaai
                  cvpr (iccv wacv) ieee acm nature. --column = the figure sits in one column, not the full width.
                  --placed-mm / --min-pt / --max-pt / --min-line-pt override the preset.
needs:  pip install playwright && python3 -m playwright install chromium
"""
import argparse, pathlib, re, sys
from playwright.sync_api import sync_playwright

# venue: (full text width mm, one-column width mm or None, min text pt, max text pt or None, min line pt)
# Widths come from each venue's template. Where a venue states no minimum text size the value is this
# script's default (marked *). The venue table of the skill lists what each venue states.
VENUES = {
    "icml":    (171.45, 82.55, 9.0, None, 0.5),    # 9 pt* = caption size; 0.5 pt lines are an ICML rule
    "neurips": (139.7, None, 8.0, None, 0.5),      # single column, 5.5 in; 8 pt*
    "iclr":    (139.7, None, 8.0, None, 0.5),      # single column, 5.5 in; 8 pt*
    "acl":     (160.0, 77.0, 9.0, None, 0.5),      # A4, 7.7 cm columns; 9 pt*
    "aaai":    (177.2, 83.8, 9.0, None, 0.5),      # 9 pt text and 0.5 pt lines are AAAI rules
    "cvpr":    (174.6, 82.55, 9.0, None, 0.5),     # 9 pt*; the guide says to match the 10 pt body text
    "ieee":    (181.9, 88.9, 8.0, None, 0.5),      # 7.16 in / 3.5 in; 8 pt*
    "acm":     (177.9, 84.8, 8.0, None, 0.5),      # acmart sigconf; 8 pt*
    "nature":  (183.0, 89.0, 5.0, 7.0, 0.25),      # 5-7 pt text and 0.25-1 pt lines are Nature rules
}
ALIASES = {"emnlp": "acl", "naacl": "acl", "eacl": "acl", "aacl": "acl", "iccv": "cvpr", "wacv": "cvpr"}


def apply_venue(a):
    """fill placed_mm / min_pt / max_pt / min_line_pt from --venue unless given explicitly."""
    if a.venue:
        full, col, mn, mx, ln = VENUES[ALIASES.get(a.venue, a.venue)]
    elif a.placed_mm is None or a.min_pt is None:
        sys.exit("give --venue NAME, or --placed-mm WIDTH and --min-pt SIZE: text is judged at its printed size")
    else:
        full, col, mn, mx, ln = a.placed_mm, None, a.min_pt, None, 0.5
    if a.column and col is None:
        sys.exit(f"{a.venue} is a single-column venue: drop --column" if a.venue else
                 "--column needs --venue; with --placed-mm, pass the column width itself")
    if a.placed_mm is None:
        a.placed_mm = col if a.column else full
    a.min_pt = mn if a.min_pt is None else a.min_pt
    a.max_pt = mx if a.max_pt is None else a.max_pt
    a.min_line_pt = ln if a.min_line_pt is None else a.min_line_pt
    if a.venue:
        cap = f", <= {a.max_pt:g} pt" if a.max_pt else ""
        print(f"venue {a.venue}: placed {a.placed_mm:g} mm, text >= {a.min_pt:g} pt{cap}, lines >= {a.min_line_pt:g} pt")


RISKY = set("✓✗✔✘✦★☆⇒⇐⇔→←↑↓●○◆◇")

JS = r"""
() => {
  const SKIP = 'marker, defs, symbol, title, desc, style, script, [aria-hidden="true"]';
  const els = [...document.body.querySelectorAll('*')].filter(e => !e.closest(SKIP));
  let W = 0, H = 0;
  for (const e of els) { const r = e.getBoundingClientRect(); W = Math.max(W, r.right); H = Math.max(H, r.bottom); }
  const kids = [...document.body.children].filter(e => !['STYLE', 'SCRIPT', 'META', 'LINK', 'TITLE'].includes(e.tagName));
  const root = kids.length === 1 ? kids[0] : null;           // the figure's root (svg, or the artboard div)
  if (root) {
    const r = root.getBoundingClientRect();
    if (r.width < window.innerWidth) { W = r.right; H = r.bottom; }
  }
  const isBox = el => {
    const cs = getComputedStyle(el);
    if (el instanceof SVGElement) return false;
    const bw = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth);
    const bg = cs.backgroundColor;
    return bw > 0 || (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent');
  };
  const texts = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = tw.nextNode())) {
    const s = n.textContent.replace(/\s+/g, ' ').trim();
    if (!s) continue;
    const el = n.parentElement;
    if (!el || el.closest(SKIP)) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    const rects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
    if (!rects.length) continue;
    let fs = parseFloat(getComputedStyle(el).fontSize);
    if (el instanceof SVGElement) {           // font size in screen px = user units x CTM scale
      const m = el.getScreenCTM(); if (m) fs *= Math.hypot(m.a, m.b);
    }
    let box = null;
    if (el instanceof SVGElement) {           // SVG text: the smallest drawn rect that contains its centre
      const c = range.getBoundingClientRect(), cx = (c.left + c.right) / 2, cy = (c.top + c.bottom) / 2;
      let best = null, area = Infinity;
      for (const q of document.querySelectorAll('svg rect')) {
        if (q.closest(SKIP)) continue;
        const qs = getComputedStyle(q);
        if (qs.fill === 'none' && qs.stroke === 'none') continue;
        const r = q.getBoundingClientRect();
        if (cx > r.left && cx < r.right && cy > r.top && cy < r.bottom && r.width * r.height < area) {
          area = r.width * r.height; best = {l: r.left, t: r.top, r: r.right, b: r.bottom};
        }
      }
      if (best && area < W * H * 0.5) box = best;
    }
    for (let a = el; !box && a && a !== document.body; a = a.parentElement) {
      if (isBox(a)) { const r = a.getBoundingClientRect(); box = {l: r.left, t: r.top, r: r.right, b: r.bottom}; break; }
    }
    let bg = 'rgb(255, 255, 255)';
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) {
      const c = getComputedStyle(a).backgroundColor;
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') { bg = c; break; }
    }
    const blk = el.closest('text') || el.closest('div') || el;
    const whole = (blk.textContent || s).replace(/\s+/g, ' ').trim();
    for (const r of rects)
      texts.push({s, fs, l: r.left, t: r.top, r: r.right, b: r.bottom, box, bg, whole});
  }
  const lines = [];
  for (const e of document.querySelectorAll('svg line, svg polyline, svg path')) {
    if (e.closest(SKIP)) continue;
    const cs = getComputedStyle(e);
    if (e.tagName === 'path' && cs.fill !== 'none') continue;
    if (cs.stroke === 'none' || parseFloat(cs.strokeWidth) === 0) continue;
    const r = e.getBoundingClientRect();
    const w = Math.max(1.5, parseFloat(cs.strokeWidth) / 2);   // a straight line's bbox has no thickness
    lines.push({l: r.left - w, t: r.top - w, r: r.right + w, b: r.bottom + w, tag: e.tagName});
  }
  const strokes = [];
  for (const e of document.querySelectorAll('svg line, svg polyline, svg path, svg polygon, svg rect, svg circle, svg ellipse')) {
    if (e.closest(SKIP)) continue;
    const cs = getComputedStyle(e);
    if (cs.stroke === 'none' || cs.visibility === 'hidden') continue;
    const sw = parseFloat(cs.strokeWidth); if (!sw) continue;
    const m = e.getScreenCTM(); const sc = m ? Math.hypot(m.a, m.b) : 1;
    strokes.push({w: sw * sc, what: e.tagName});
  }
  const boxes = [];
  const figRoot = root || document.body.firstElementChild;
  for (const e of document.querySelectorAll('div, span')) {
    if (e === figRoot || e.closest(SKIP)) continue;
    const cs = getComputedStyle(e);
    const bw = parseFloat(cs.borderTopWidth) || 0;
    if (bw > 0 && cs.borderTopStyle !== 'none')
      strokes.push({w: bw, what: 'border of ' + (e.textContent || '').trim().slice(0, 24)});
    if (cs.position !== 'absolute') continue;
    const vis = bw > 0 || (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent');
    if (!vis) continue;
    const r = e.getBoundingClientRect();
    if (r.width > W * 0.6) continue;                       // zones and boundaries are not aligned objects
    if (!(e.textContent || '').trim()) continue;            // stacked shadows, tensor cells: offsets are intentional
    boxes.push({cx: (r.left + r.right) / 2, cy: (r.top + r.bottom) / 2, l: r.left, r: r.right, t: r.top, b: r.bottom,
                s: (e.textContent || '').trim().slice(0, 20)});
  }
  return {W, H, texts, lines, strokes, boxes};
}
"""


def inter(a, b, pad=0.0):
    return min(a["r"], b["r"]) - max(a["l"], b["l"]) > pad and min(a["b"], b["b"]) - max(a["t"], b["t"]) > pad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fig")
    ap.add_argument("--venue", choices=sorted(VENUES) + sorted(ALIASES), help="preset width and limits for a venue")
    ap.add_argument("--column", action="store_true", help="the figure is placed in one column (default: full text width)")
    ap.add_argument("--placed-mm", type=float, help="printed width in mm (overrides the venue preset)")
    ap.add_argument("--min-pt", type=float, help="smallest allowed text in pt (overrides the venue preset)")
    ap.add_argument("--max-pt", type=float, help="largest allowed text (Nature: 7); single letters up to +1.5pt pass as panel labels")
    ap.add_argument("--png", help="also save a 2x render here")
    ap.add_argument("--compare", help="original figure: every label in it must still exist in FIG")
    ap.add_argument("--min-line-pt", type=float, help="thinnest allowed line at print size (default 0.5, or the venue preset)")
    ap.add_argument("--cvd", help="write PREFIX_gray/_deutan/_protan.png colour-vision checks")
    a = ap.parse_args()
    apply_venue(a)

    png = a.png or (a.cvd + "_render.png" if a.cvd else None)
    d = render(pathlib.Path(a.fig).resolve(), png)
    if a.cvd:
        cvd_images(png, a.cvd)
    old = render(pathlib.Path(a.compare).resolve()) if a.compare else None
    report(d, a, old)


def render(path, png=None):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 3000, "height": 2000}, device_scale_factor=2)
        src = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".svg":      # a bare SVG has no <body>: wrap it in a page
            src = '<!doctype html><html><body style="margin:0">' + src + "</body></html>"
        elif path.name.endswith(".dc.html"):   # Claude Design board: drop the runtime, keep the literal markup
            src = re.sub(r"<script\b.*?</script>", "", src, flags=re.S | re.I)
            for t in ("<x-dc>", "</x-dc>", "<helmet>", "</helmet>"):
                src = src.replace(t, "")
        tmp = path.with_name("._audit_" + path.name.replace(".dc.html", ".html").replace(".svg", ".html"))
        tmp.write_text(src, encoding="utf-8")
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(400)
        d = pg.evaluate(JS)
        if png:
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": d["W"], "height": d["H"]})
        b.close()
        tmp.unlink(missing_ok=True)
    return d


def grey_bg(css):
    """grey = low chroma and not white; light pastel zones (some chroma) and white pass."""
    nums = [float(x) for x in re.findall(r"[\d.]+", css)[:3]]
    if len(nums) < 3:
        return None
    r, g, b = nums
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    chroma = (max(nums) - min(nums)) / 255
    return f"rgb({r:.0f},{g:.0f},{b:.0f})" if chroma < 0.04 and lum < 0.96 else None


def cvd_images(png, prefix):
    """grayscale + Machado et al. (2009) deuteranopia / protanopia (severity 1.0) simulations."""
    import numpy as np
    from PIL import Image
    im = Image.open(png).convert("RGB")
    im.convert("L").save(prefix + "_gray.png")
    M = {"deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
         "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]}
    a = np.asarray(im).astype(np.float64) / 255
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    for name, m in M.items():
        o = np.clip(lin @ np.array(m).T, 0, 1)
        s = np.where(o <= 0.0031308, o * 12.92, 1.055 * o ** (1 / 2.4) - 0.055)
        Image.fromarray((s * 255).round().astype("uint8")).save(f"{prefix}_{name}.png")
    print(f"CVD   wrote {prefix}_gray.png, {prefix}_deutan.png, {prefix}_protan.png -- look at them")


def labels(d):
    """whole labels (a label styled in parts, e.g. 'Parameter <i>A</i>', counts as one)."""
    return {" ".join(t.get("whole", t["s"]).split()).lower() for t in d["texts"]}


def report(d, a, old=None):
    W = d["W"]
    k = a.placed_mm / 25.4 * 72 / W            # px on screen -> printed pt
    err, warn = [], []
    sizes = []
    for t in d["texts"]:
        pt = t["fs"] * k
        sizes.append(pt)
        if pt < a.min_pt - 1e-6:
            err.append(f"small text {pt:.2f}pt (<{a.min_pt}): '{t['s'][:40]}'")
        if a.max_pt and pt > a.max_pt + 1e-6 and not (len(t["s"].strip()) == 1 and pt <= a.max_pt + 1.5):
            err.append(f"large text {pt:.2f}pt (>{a.max_pt}): '{t['s'][:40]}'")
        if t["r"] > W + 0.5 or t["b"] > d["H"] + 0.5 or t["l"] < -0.5 or t["t"] < -0.5:
            err.append(f"outside canvas: '{t['s'][:40]}'")
        bx = t["box"]
        if bx:
            mates = [u for u in d["texts"] if u["box"] == bx and abs(u["t"] - t["t"]) < 2]   # runs on the same line
            ll, rr = min(u["l"] for u in mates), max(u["r"] for u in mates)
            over = max(bx["l"] - t["l"], t["r"] - bx["r"], bx["t"] - t["t"], t["b"] - bx["b"])
            if over > 0.5:
                err.append(f"text spills out of its box by {over:.1f}px: '{t['s'][:40]}'")
            else:
                gap = min(ll - bx["l"], bx["r"] - rr)
                if gap < 6:
                    warn.append(f"text hugs box edge ({gap:.1f}px): '{t['s'][:40]}'")
        for ln in d["lines"]:
            if inter(t, ln, 0.5) and (ln["r"] - ln["l"] < 8 or ln["b"] - ln["t"] < 8):
                warn.append(f"text crosses a {ln['tag']}: '{t['s'][:40]}'")
                break
        bad = sorted(set(t["s"]) & RISKY)
        if bad:
            warn.append(f"font-fallback glyph {''.join(bad)} in '{t['s'][:40]}' -> draw it as a path")
        g = grey_bg(t.get("bg", "rgb(255, 255, 255)"))
        if g:
            warn.append(f"text on a grey background ({g}): '{t['s'][:40]}'")
    thin = {}
    for st in d.get("strokes", []):
        pt_w = st["w"] * k
        if pt_w < a.min_line_pt - 1e-6:
            thin.setdefault(st["what"].split(" of ")[0], []).append((pt_w, st["what"]))
    for kind, items in thin.items():
        lo = min(w for w, _ in items)
        warn.append(f"{len(items)} {kind} line(s) thinner than {a.min_line_pt}pt (thinnest {lo:.2f}pt, e.g. '{items[0][1][:40]}')")
    Bx = d.get("boxes", [])
    for i in range(len(Bx)):
        for j in range(i + 1, len(Bx)):
            p, q = Bx[i], Bx[j]
            dy, dx = abs(p["cy"] - q["cy"]), abs(p["cx"] - q["cx"])
            side = p["r"] < q["l"] or q["r"] < p["l"]             # side by side -> should share a centre line
            stacked = p["b"] < q["t"] or q["b"] < p["t"]
            if side and 0.5 < dy <= 6:
                warn.append(f"row almost aligned (centres {dy:.1f}px apart): '{p['s']}' / '{q['s']}'")
            if stacked and 0.5 < dx <= 6:
                warn.append(f"column almost aligned (centres {dx:.1f}px apart): '{p['s']}' / '{q['s']}'")
    T = d["texts"]
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            if inter(T[i], T[j], 1.0):
                err.append(f"text overlap: '{T[i]['s'][:30]}' x '{T[j]['s'][:30]}'")

    if old is not None:
        new_l = labels(d)
        gone = sorted(labels(old) - new_l)
        added = sorted(new_l - labels(old))
        for g in gone:
            err.append(f"structure: label of the original is missing: '{g}'")
        if added:
            print("INFO  labels added vs original:", "; ".join(added))

    sizes.sort()
    print(f"canvas {W:.0f}x{d['H']:.0f}px placed at {a.placed_mm}mm -> 1px = {k:.3f}pt")
    if sizes:
        print(f"printed text: min {sizes[0]:.2f}pt  median {sizes[len(sizes)//2]:.2f}pt  max {sizes[-1]:.2f}pt  ({len(sizes)} runs)")
    for m in dict.fromkeys(err):
        print("ERROR", m)
    for m in dict.fromkeys(warn):
        print("WARN ", m)
    print("RESULT", "FAIL" if err else "PASS", f"({len(set(err))} errors, {len(set(warn))} warnings)")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
