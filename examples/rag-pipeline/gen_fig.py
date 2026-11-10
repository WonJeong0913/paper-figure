#!/usr/bin/env python3
"""Example: a generic retrieval-augmented generation pipeline, drawn for ICML (9 pt minimum).

Run from this folder:  python3 gen_fig.py
Then:                  python3 ../../scripts/figure_audit.py project/Main.dc.html --venue icml
                       python3 ../../scripts/dc_export.py . --out out --venue icml
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _common import write_canvas
from dc_board import Board, STYLE

b = Board(1584, 370, font=30)           # 1584 px placed at 171.45 mm -> 30 px = 9.2 pt
Y, H = 120, 90                          # one row of modules; arrows run through its centre
C = Y + H // 2

b.card(160, Y, 210, H, "Query<br>Encoder")
b.card(520, Y, 180, H, "Retriever")
b.card(870, Y, 180, H, "Reranker")
b.card(1210, Y, 190, H, "Generator", kind="core")      # the module the paper is about
b.tag(520, 290, 180, 56, "Corpus")                     # external resource: white tag, dashed arrow

b.arrow([(20, C), (159, C)]);     b.text(90, C - 44, "question", w=140)
b.arrow([(370, C), (519, C)]);    b.text(445, C - 44, "query", w=120)
b.arrow([(700, C), (869, C)]);    b.text(785, C - 44, "top-100", w=140)
b.arrow([(1050, C), (1209, C)]);  b.text(1130, C - 44, "passages", w=150)
b.arrow([(1400, C), (1563, C)]);  b.text(1482, C - 44, "answer", w=130)
b.arrow([(610, 290), (610, Y + H + 1)], color=STYLE["muted"], dash="2 6")

# feedback loop runs in an outer band and never crosses a module
b.arrow([(1305, Y), (1305, 62), (610, 62), (610, Y - 1)], color=STYLE["loop"], dash="7 6")
b.text(957, 16, "missing evidence", w=260, color=STYLE["loop"])

write_canvas(b.save("project/Main.dc.html", "Fig. 1 — RAG pipeline (example)"))
