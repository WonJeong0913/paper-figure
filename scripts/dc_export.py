#!/usr/bin/env python3
"""Export Claude Design artboards (project/*.dc.html) to paper-ready files.

For each board: <out>/<stem>.pdf  vector PDF, exactly w x h px (text stays text)  -> LaTeX \\includegraphics
                <out>/<stem>.png  300 dpi at the placed width                     -> Word / slides
                <out>/<stem>_preview.png  1x render for a quick look
w x h come from project/canvas.json (boards[...]). The DC runtime (support.js) is not needed:
scripts and the <x-dc>/<helmet> wrappers are stripped, the literal markup is rendered as is,
so figure boards must not use {{holes}} or <sc-for> (write every element out).

usage:  python3 dc_export.py ROOT [BOARD ...] [--out paperfigs] (--venue icml [--column] | --placed-mm 165)
        ROOT = folder that holds project/canvas.json; BOARD = e.g. Fig2.dc.html (default: all boards)
After export, each PDF is checked with poppler (if installed): every font embedded, and no raster
images (a diagram PDF should be pure vector; spark-to-paper's acceptance rule).
needs:  pip install playwright && python3 -m playwright install chromium   (poppler-utils for the PDF check)
"""
import argparse, json, pathlib, re, shutil, subprocess, sys
from playwright.sync_api import sync_playwright


# venue: (full text width mm, one-column width mm or None); same table as figure_audit.py
WIDTHS = {"icml": (171.45, 82.55), "neurips": (139.7, None), "iclr": (139.7, None), "acl": (160.0, 77.0),
          "aaai": (177.2, 83.8), "cvpr": (174.6, 82.55), "ieee": (181.9, 88.9), "acm": (177.9, 84.8),
          "nature": (183.0, 89.0)}
ALIASES = {"emnlp": "acl", "naacl": "acl", "eacl": "acl", "aacl": "acl", "iccv": "cvpr", "wacv": "cvpr"}


def flatten(src: str) -> str:
    s = re.sub(r"<script\b.*?</script>", "", src, flags=re.S | re.I)
    for t in ("<x-dc>", "</x-dc>", "<helmet>", "</helmet>"):
        s = s.replace(t, "")
    if "{{" in s:
        print("  WARN  {{hole}} left in the markup: it prints literally; write the value out", file=sys.stderr)
    return s


def pdf_check(pdf):
    """fonts all embedded (emb=yes) and zero raster images; returns a list of problems."""
    probs = []
    if shutil.which("pdffonts"):
        rows = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
        for r in rows:
            cols = r.split()
            if len(cols) >= 5 and cols[-5] == "no":          # columns: ... emb sub uni object-id gen
                probs.append(f"font not embedded: {cols[0]}")
            if "Type 3" in r:
                probs.append(f"Type 3 font (AAAI forbids these and other venues reject them; list a TrueType font such as Arial first): {cols[0]}")
    else:
        probs.append("pdffonts not installed: font embedding not checked")
    if shutil.which("pdfimages"):
        imgs = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
        if imgs:
            probs.append(f"{len(imgs)} raster image(s) inside the PDF (expected 0 for a vector diagram)")
    return list(dict.fromkeys(probs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("boards", nargs="*")
    ap.add_argument("--out", default="paperfigs")
    ap.add_argument("--venue", choices=sorted(WIDTHS) + sorted(ALIASES), help="take the printed width from a venue preset")
    ap.add_argument("--column", action="store_true", help="the figure is placed in one column (default: full text width)")
    ap.add_argument("--placed-mm", type=float, help="printed width in mm; sets the PNG pixel size (overrides the venue preset)")
    a = ap.parse_args()
    if a.placed_mm is None:
        if not a.venue:
            sys.exit("give --venue NAME or --placed-mm WIDTH: the PNG is rendered at 300 dpi for that width")
        full, col = WIDTHS[ALIASES.get(a.venue, a.venue)]
        if a.column and col is None:
            sys.exit(f"{a.venue} is a single-column venue: drop --column")
        a.placed_mm = col if a.column else full

    root = pathlib.Path(a.root).resolve()
    canvas = json.loads((root / "project/canvas.json").read_text(encoding="utf-8"))
    boards = a.boards or canvas.get("order") or list(canvas["boards"])
    out = pathlib.Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_flat"
    tmp.mkdir(exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch()
        for name in boards:
            meta = canvas["boards"][name]
            w, h = int(meta["w"]), int(meta["h"])
            stem = pathlib.Path(name).name.replace(".dc.html", "")
            flat = tmp / f"{stem}.html"
            flat.write_text(flatten((root / "project" / name).read_text(encoding="utf-8")), encoding="utf-8")

            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(flat.as_uri())
            pg.wait_for_timeout(300)
            sw, shh = pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
            if sw > w or shh > h:
                print(f"  WARN  {name}: content {sw}x{shh} is larger than the board {w}x{h}; it will be cut", file=sys.stderr)
            pg.pdf(path=str(out / f"{stem}.pdf"), width=f"{w}px", height=f"{h}px",
                   print_background=True, page_ranges="1")
            pg.screenshot(path=str(out / f"{stem}_preview.png"), clip={"x": 0, "y": 0, "width": w, "height": h})
            pg.close()

            scale = a.placed_mm / 25.4 * 300 / w          # px per CSS px for 300 dpi at the placed width
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
            pg.goto(flat.as_uri())
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(out / f"{stem}.png"), clip={"x": 0, "y": 0, "width": w, "height": h})
            pg.close()
            print(f"{name}: {w}x{h}px -> {stem}.pdf, {stem}.png ({round(w * scale)}x{round(h * scale)}px = 300dpi at {a.placed_mm}mm)")
            for p in pdf_check(out / f"{stem}.pdf"):
                print(f"  CHECK {p}")
        b.close()


if __name__ == "__main__":
    main()
