#!/usr/bin/env python3
"""Example (vocabulary B, architecture figure): a pre-LN decoder-only Transformer.
Shape says type: trapezoid = linear projection, rounded rectangle = sequence transform,
circle = elementwise operation. Drawn for ICML: 30 px text prints at 9.2 pt.

  python3 gen_fig.py
  python3 ../../scripts/figure_audit.py project/Main.dc.html --venue icml
  python3 ../../scripts/dc_export.py . --out out --venue icml
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _common import write_canvas
from dc_board import Board, STYLE

b = Board(1584, 410, font=30)
T, U = 310, 180                           # residual stream (trunk) and the sub-layer row above it

# repeated block: a zone with copies behind it, name + count at its top left
b.zone(310, 40, 880, 350, depth=2, fill="#FFFFFF")
b.header_pill(334, 54, "Decoder block", 200, "×N", 84)

# input, embedding, output head
b.cells(40, T - 39, 3, cell=26)
b.math(53, T - 92, "x")
b.arrow([(66, T), (119, T)])
b.trap(120, T - 50, 150, 100, "Embed", expand=True)
b.op(1280, T, "N")
b.trap(1340, T - 50, 180, 100, "Unembed", expand=True)
b.math(1545, T - 50, "y", w=50)

# residual stream: one straight trunk, sub-layers branch off and rejoin at +
b.arrow([(270, T), (714, T)])
b.arrow([(775, T), (1079, T)])
b.arrow([(1140, T), (1249, T)])
b.arrow([(1310, T), (1339, T)])
b.arrow([(1520, T), (1572, T)])
b.text(565, T + 14, "residual stream", w=230)

# sub-layer 1: norm -> self-attention -> add
b.dot(350, T)
b.arrow([(350, T), (350, U), (384, U)])
b.op(415, U, "N")
b.arrow([(445, U), (469, U)])
b.card(470, U - 45, 230, 90, "Self-Attention", kind="core")
b.arrow([(700, U), (745, U), (745, T - 31)])
b.op(745, T, "+")

# sub-layer 2: norm -> MLP (expand, contract) -> add
b.dot(815, T)
b.arrow([(815, T), (815, U), (849, U)])
b.op(880, U, "N")
b.arrow([(910, U), (934, U)])
b.trap(935, U - 45, 62, 90, expand=True)
b.trap(1003, U - 45, 62, 90, expand=False)
b.text(1000, U - 88, "MLP", w=90, bold=True, color=STYLE["proj"][2])
b.arrow([(1065, U), (1110, U), (1110, T - 31)])
b.op(1110, T, "+")

# legend for the two operation symbols (also state it in the caption)
b.op(1262, 86, "N", d=46);  b.text(1296, 68, "layer norm", w=170, align="left")
b.op(1262, 146, "+", d=46);  b.text(1296, 128, "add", w=80, align="left")

write_canvas(b.save("project/Main.dc.html", "Fig. 1 — Decoder-only Transformer (example)"))
