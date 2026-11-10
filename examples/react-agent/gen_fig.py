#!/usr/bin/env python3
"""Example (vocabulary A, system figure): a ReAct-style tool-using agent [Yao et al., ICLR 2023].
Drawn at Nature size (183 mm, text 5-7 pt): 21 px text prints at 6.9 pt.

  python3 gen_fig.py
  python3 ../../scripts/figure_audit.py project/Main.dc.html --venue nature
  python3 ../../scripts/dc_export.py . --out out --venue nature
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _common import write_canvas
from dc_board import Board, STYLE

b = Board(1584, 440, font=21)
C = 215                                   # centre line of the main row
BLUE = "#185FA5"

# scopes: what the LLM does, what the tools do
b.panel(430, 110, 270, 210, "LLM", icon="spark", kind="core", fill=STYLE["zone"])
b.panel(830, 110, 240, 210, "Tools", icon="gear")

# modules
b.badge(44, C, "User")
b.icon_card(166, 140, 150, 150, "Prompt<br>Assembly", "layers")
b.icon_card(450, 135, 230, 160, "Reasoning &amp;<br>Action Selection", "spark", kind="core",
            chips=[("thought", "core"), ("action", "core")])
b.icon_card(850, 128, 200, 50, "Search", "search", side=True)
b.icon_card(850, 190, 200, 50, "Calculator", "calc", side=True)
b.icon_card(850, 252, 200, 50, "Code Runner", "code", side=True)
b.icon_card(1190, 140, 150, 150, "Answer<br>Formatting", "send")
b.badge(1536, C, "User")
b.bar(166, 376, 904, 46, "Trajectory: thought, action, observation per step")

# main flow: arrows carry data names
b.arrow([(72, C), (165, C)]);      b.text(118, C - 34, "question", w=110)
b.arrow([(316, C), (449, C)]);     b.text(373, C - 34, "prompt", w=100)
b.arrow([(680, C), (829, C)], color=STYLE["accent_line"])
b.text(755, C - 59, "<b>CALL</b><br>tool, input", w=140, color=STYLE["accent"])
b.arrow([(1340, C), (1507, C)]);   b.text(1424, C - 34, "answer", w=100)

# decision FINISH leaves the LLM and skips the tools (outer band, never crosses a module)
b.arrow([(620, 135), (620, 48), (1265, 48), (1265, 139)], color=BLUE)
b.text(942, 14, "<b>FINISH</b>: final answer", w=300, color=BLUE)

# state: each step is written to the trajectory, which feeds the next prompt (the loop)
b.arrow([(565, 295), (565, 375)]);  b.text(577, 335, "thought, action", w=170, align="left")
b.arrow([(950, 320), (950, 375)]);  b.text(962, 335, "observation", w=130, align="left")
b.arrow([(241, 376), (241, 291)], color=STYLE["loop"], dash="7 6")
b.text(253, 322, "trajectory", w=120, color=STYLE["loop"], align="left")

write_canvas(b.save("project/Main.dc.html", "Fig. 1 — ReAct agent loop (example)"))
