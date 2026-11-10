"""Shared by the example generators: import path for scripts/ and a one-board canvas.json writer."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))


def write_canvas(meta, name="Main.dc.html", title="paper-figure example"):
    pathlib.Path("project/canvas.json").write_text(json.dumps({
        "v": 3, "title": title, "launch": {"view": "canvas"}, "pages": [], "notes": {}, "designSystems": [],
        "boards": {name: {"x": 0, "y": 0, **meta}}, "order": [name]}, indent=2), encoding="utf-8")
