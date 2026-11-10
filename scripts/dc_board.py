#!/usr/bin/env python3
"""Build Claude Design boards (.dc.html) for paper figures with the diagrams.md invariants built in.

Every element is a separate absolutely-positioned node (editable on the canvas); arrows are one small
<svg> per straight segment (diagrams.md formulas); colours/strokes come from one STYLE dict per paper.

  from dc_board import Board, STYLE
  b = Board(1584, 520, font=30)                      # 1584 px placed at 171.45 mm (ICML) -> 30 px = 9.2 pt
  b.card(140, 120, 160, 70, "Conv1d", kind="seq")    # rounded rectangle: sequence transform
  b.trap(320, 110, 170, 90, "Linear", expand=True)   # trapezoid: linear projection (wide side = more dims)
  b.op(560, 155, "σ")                                # circle: elementwise op (σ, ×, +, N)
  b.arrow([(300, 155), (319, 155)])                  # orthogonal polyline, head on the last point
  b.math(330, 100, "x")                              # variable: serif italic (ML venues)
  b.save("canvas/project/Main.dc.html", "Fig. 1")
"""
import pathlib

STYLE = {  # one style sheet per paper; change here, never per element
    "font": "Arial, 'Liberation Sans', 'Helvetica Neue', sans-serif",   # TrueType first: OTF/CFF fonts become Type 3 in Chromium PDFs
    "math": "'Times New Roman', 'Nimbus Roman', 'Liberation Serif', serif",
    "ink": "#2C2C2A", "label": "#3D3D3A", "muted": "#6B6A64",
    "neutral": ("#FFFFFF", "#5B6472", "#2C2C2A"),   # fill, stroke, text
    "seq": ("#F3F1FE", "#7F77DD", "#26215C"),       # sequence transforms (SSM, Conv, attention)
    "core": ("#F3F1FE", "#7F77DD", "#26215C"),      # the paper's contribution (thicker stroke)
    "proj": ("#EAF1F8", "#4A6FA5", "#1F3552"),      # linear projections (trapezoids)
    "accent": "#534AB7", "accent_line": "#7F77DD",  # selection / key path
    "loop": "#D55E00",                              # recurrence / feedback (Okabe-Ito vermillion)
    "zone": "#F6F4FF", "zone_line": "#CFCBF1", "boundary": "#9A988F",
    "panel": "#F5F6F8",                             # neutral panel fill; never put text directly on it
    "tool": ("#FFFFFF", "#5B6472", "#2C2C2A"), "go": ("#EAF3FC", "#378ADD", "#042C53"),   # tools; the accepted / output path
    "stroke": 2,                                    # whole px only: Chromium floors CSS borders (1.8 -> 1 px = 0.30 pt)
    "line": 2.4,                                    # connector width (0.73 pt)
}


ICONS = {  # 24x24 stroke icons for system / agent figures (vocabulary A); add your own paths here
    "user": '<circle cx="12" cy="8.5" r="4"/><path d="M4.5 20.5 A7.5 7.5 0 0 1 19.5 20.5"/>',
    "chat": '<path d="M4 5 H20 V16 H10 L6 20 V16 H4 Z"/><path d="M8.6 10.5 h0.01 M12 10.5 h0.01 M15.4 10.5 h0.01" stroke-width="2.4"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15 L20.5 20.5"/>',
    "doc": '<path d="M6 3 H14 L18.5 7.5 V21 H6 Z"/><path d="M14 3 V7.5 H18.5"/><path d="M9 12 H15.5 M9 15.5 H15.5"/>',
    "database": '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6 V18 C5 19.4 8.1 20.6 12 20.6 C15.9 20.6 19 19.4 19 18 V6"/><path d="M5 12 C5 13.4 8.1 14.6 12 14.6 C15.9 14.6 19 13.4 19 12"/>',
    "layers": '<path d="M12 3.5 L21 8 L12 12.5 L3 8 Z"/><path d="M3 12 L12 16.5 L21 12"/><path d="M3 16 L12 20.5 L21 16"/>',
    "send": '<path d="M21 3 L3 10.5 L10 13.5 L13 21 Z"/><path d="M21 3 L10 13.5"/>',
    "check": '<path d="M12 3 L19.5 6 V11.5 C19.5 16 16.3 19.4 12 21 C7.7 19.4 4.5 16 4.5 11.5 V6 Z"/><path d="M8.6 12 L11 14.4 L15.6 9.6"/>',
    "filter": '<path d="M3.5 4.5 H20.5 L14 12.5 V19 L10 21 V12.5 Z"/>',
    "branch": '<circle cx="7" cy="5.5" r="2.2"/><circle cx="7" cy="18.5" r="2.2"/><circle cx="17" cy="8.5" r="2.2"/><path d="M7 7.7 V16.3 M17 10.7 C17 14 7 12 7 16.3"/>',
    "code": '<path d="M8.5 7 L3.5 12 L8.5 17 M15.5 7 L20.5 12 L15.5 17 M13.5 5 L10.5 19"/>',
    "calc": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8.5 7.5 H15.5 M8.5 12 h0.01 M12 12 h0.01 M15.5 12 h0.01 M8.5 16.5 h0.01 M12 16.5 h0.01 M15.5 16.5 h0.01" stroke-width="2.2"/>',
    "spark": '<path d="M12 2.5 C12.6 8 16 11.4 21.5 12 C16 12.6 12.6 16 12 21.5 C11.4 16 8 12.6 2.5 12 C8 11.4 11.4 8 12 2.5 Z"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2.5 V5 M12 19 V21.5 M2.5 12 H5 M19 12 H21.5 M5.3 5.3 L7 7 M17 17 L18.7 18.7 M18.7 5.3 L17 7 M7 17 L5.3 18.7"/>',
    "loop": '<path d="M19.5 12 A7.5 7.5 0 1 1 17.3 6.7"/><path d="M19.6 3.6 V7.6 H15.6"/>',
}


class Board:
    def __init__(self, w, h, font=30, style=STYLE):
        self.w, self.h, self.f, self.s = w, h, font, style
        self.back, self.arrows, self.shapes, self.labels = [], [], [], []
        self.mid = 0

    # ---------- containers ----------
    def region(self, l, t, w, h, fill=None, dashed=False):
        """zone (light fill, no border) or dashed boundary (logical scope)."""
        st = (f"background: {fill}; border: 0px solid transparent; border-radius: 16px" if fill and not dashed else
              f"background: transparent; border: 2px dashed {self.s['boundary']}; border-radius: 18px")
        self.back.append(self._div(l, t, w, h, st))

    def stack(self, l, t, w, h, depth=2, kind="core", step=8):
        """repetition: copies offset up-right, drawn behind the real card (pair with bracket())."""
        _, stroke, _ = self.s[kind]
        for i in range(depth, 0, -1):
            self.back.append(self._div(l + i * step, t - i * step, w, h,
                                       f"background: #FFFFFF; border: {self.s['stroke']}px solid {stroke}; border-radius: 12px"))

    # ---------- shapes ----------
    def card(self, l, t, w, h, title, sub=None, kind="neutral", dashed=False, size=None):
        fill, stroke, color = self.s[kind]
        bw = self.s["stroke"]                     # emphasis comes from fill/colour, not a heavier border
        sub_html = f'<br><span style="font-weight: 400">{sub}</span>' if sub else ""
        self.shapes.append(self._div(l, t, w, h,
            f"padding: 6px 10px; display: flex; align-items: center; justify-content: center; text-align: center; "
            f"background: {fill}; border: {bw}px {'dashed' if dashed else 'solid'} {stroke}; border-radius: 12px; "
            f"font-size: {size or self.f}px; line-height: {round((size or self.f) * 1.2)}px; font-weight: 700; color: {color}; "
            f"white-space: nowrap", f"<span>{title}{sub_html}</span>"))

    def trap(self, l, t, w, h, text="", expand=True, kind="proj", inset=None):
        """linear projection as a trapezoid; expand=True: narrow input side on the left (dims grow)."""
        fill, stroke, color = self.s[kind]
        k = inset if inset is not None else round(h * 0.22)
        pts = f"1,{k} {w - 1},1 {w - 1},{h - 1} 1,{h - k}" if expand else f"1,1 {w - 1},{k} {w - 1},{h - k} 1,{h - 1}"
        self.shapes.append(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; '
                           f'left: {l}px; top: {t}px; width: {w}px; height: {h}px; overflow: visible"><polygon points="{pts}" '
                           f'fill="{fill}" stroke="{stroke}" stroke-width="{self.s["stroke"]}" stroke-linejoin="round"/></svg>')
        if text:
            self.labels.append(self._div(l, t, w, h, f"display: flex; align-items: center; justify-content: center; "
                                         f"font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; font-weight: 700; "
                                         f"color: {color}; white-space: nowrap", f"<span>{text}</span>"))

    def op(self, cx, cy, sym, d=60, kind="neutral"):
        """elementwise operation: circle with a serif symbol (σ, ×, +, N)."""
        fill, stroke, color = self.s[kind]
        self.shapes.append(self._div(cx - d // 2, cy - d // 2, d, d,
            f"display: flex; align-items: center; justify-content: center; background: {fill}; "
            f"border: {self.s['stroke']}px solid {self.s['ink']}; border-radius: 50%; font-family: {self.s['math']}; "
            f"font-size: {self.f + 4}px; line-height: {self.f + 4}px; color: {self.s['ink']}", f"<span>{sym}</span>"))

    def cells(self, l, t, n, cell=26, vertical=True, kind="proj", hi=None):
        """a tensor / vector drawn as n cells; hi = index of a highlighted cell (e.g. the current token)."""
        fill, stroke, _ = self.s[kind]
        for i in range(n):
            x, y = (l, t + i * cell) if vertical else (l + i * cell, t)
            f = stroke if hi == i else fill
            self.shapes.append(self._div(x, y, cell, cell, f"background: {f}; border: {self.s['stroke']}px solid {stroke}"))

    def tag(self, l, t, w, h, text):
        """external resource / parameter: white with a grey border (ICML: no text on grey backgrounds)."""
        self.shapes.append(self._div(l, t, w, h,
            f"padding: 0 14px; display: flex; align-items: center; justify-content: center; background: #FFFFFF; "
            f"border: {self.s['stroke']}px solid {self.s['boundary']}; border-radius: 10px; font-size: {self.f}px; "
            f"line-height: {round(self.f * 1.2)}px; font-weight: 700; color: {self.s['label']}; white-space: nowrap", f"<span>{text}</span>"))

    # ---------- text ----------
    def text(self, x, t, html, w=300, color=None, bold=False, size=None, align="center", italic=False):
        left = x - w // 2 if align == "center" else x
        st = (f"text-align: {align}; font-size: {size or self.f}px; line-height: {round((size or self.f) * 1.2)}px; "
              f"color: {color or self.s['label']}; white-space: nowrap" + ("; font-weight: 700" if bold else "") +
              ("; font-style: italic" if italic else ""))
        self.labels.append(self._div(left, t, w, None, st, html))

    def math(self, x, t, html, w=120, color=None, size=None, align="center"):
        """variable / data name on a line: serif italic (keep sans-serif only for Nature)."""
        left = x - w // 2 if align == "center" else x
        sz = size or self.f + 4
        self.labels.append(self._div(left, t, w, None,
            f"text-align: {align}; font-family: {self.s['math']}; font-style: italic; font-size: {sz}px; "
            f"line-height: {round(sz * 1.15)}px; color: {color or self.s['ink']}; white-space: nowrap", html))

    def panel_label(self, l, t, letter):
        self.text(l, t, letter, w=40, color=self.s["ink"], bold=True, size=self.f + 4, align="left")

    def header(self, l, t, text, color=None):
        self.text(l, t, text, w=400, color=color or self.s["accent"], bold=True, align="left")

    def bracket(self, x1, x2, y, pill, text, color="#7A786F"):
        w = x2 - x1
        self.back.append(f'<svg width="{w}" height="12" viewBox="0 0 {w} 12" preserveAspectRatio="none" style="position: absolute; '
                         f'left: {x1}px; top: {y}px; width: {w}px; height: 12px; overflow: visible; fill: none; stroke: {color}; '
                         f'stroke-width: {self.s["stroke"]}; stroke-linecap: round"><path d="M 1 11 L 1 2 L {w - 1} 2 L {w - 1} 11"></path></svg>')
        self.labels.append(self._div(x1, y - round(self.f * 1.45), w, None,
            f"display: flex; justify-content: center; align-items: center; gap: 10px; font-size: {self.f}px; "
            f"line-height: {round(self.f * 1.2)}px; color: {self.s['label']}; white-space: nowrap",
            f'<span style="display: inline-flex; align-items: center; padding: 0 10px; border: {self.s["stroke"]}px solid {color}; '
            f'border-radius: {self.f}px; font-weight: 700">{pill}</span><span>{text}</span>'))

    def line(self, x1, y1, x2, y2, color=None, dash="7 6", width=None):
        """free (diagonal) guide line without a head, e.g. macro-micro zoom lines; not for data flow."""
        l, t, w, h = min(x1, x2), min(y1, y2), max(abs(x2 - x1), 1), max(abs(y2 - y1), 1)
        self.back.append(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true" '
                         f'style="position: absolute; left: {l}px; top: {t}px; width: {w}px; height: {h}px; overflow: visible; '
                         f'fill: none; stroke: {color or self.s["boundary"]}; stroke-width: {width or self.s["stroke"]}; '
                         f'stroke-dasharray: {dash}"><path d="M {x1 - l} {y1 - t} L {x2 - l} {y2 - t}"></path></svg>')

    # ---------- bottom-to-top architecture pieces ----------
    def _poly(self, l, t, w, h, pts, fill, stroke, layer):
        layer.append(f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position: absolute; '
                     f'left: {l}px; top: {t}px; width: {w}px; height: {h}px; overflow: visible"><polygon points="{pts}" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="{self.s["stroke"]}" stroke-linejoin="round"/></svg>')

    def trap_up(self, l, t, w, h, text="", widen=True, kind="proj", k=None, depth=0, step=8):
        """linear projection in a bottom-to-top flow; widen=True: narrow bottom, wide top (dims grow).
        depth > 0 draws that many copies behind it, offset up-right (x h heads)."""
        fill, stroke, color = self.s[kind]
        k = round(w * 0.15) if k is None else k
        pts = (f"{k},{h - 1} {w - k},{h - 1} {w - 1},1 1,1" if widen else f"1,{h - 1} {w - 1},{h - 1} {w - k},1 {k},1")
        for i in range(depth, 0, -1):
            self._poly(l + i * step, t - i * step, w, h, pts, "#FFFFFF", stroke, self.back)
        self._poly(l, t, w, h, pts, fill, stroke, self.shapes)
        if text:
            self.labels.append(self._div(l, t, w, h, f"display: flex; align-items: center; justify-content: center; "
                                         f"text-align: center; font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; "
                                         f"font-weight: 700; color: {color}; white-space: nowrap", f"<span>{text}</span>"))

    def dot(self, cx, cy, r=6):
        """junction where a branch leaves a line (e.g. the residual stream)."""
        self.shapes.append(self._div(cx - r, cy - r, 2 * r, 2 * r, f"background: {self.s['ink']}; border-radius: 50%"))

    def pill(self, l, t, w, text, h=46):
        """repeat count such as x N or x h: white pill, grey border."""
        self.labels.append(self._div(l, t, w, h, f"display: flex; align-items: center; justify-content: center; "
            f"background: #FFFFFF; border: {self.s['stroke']}px solid {self.s['boundary']}; border-radius: {h // 2}px; "
            f"font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; font-weight: 700; color: {self.s['label']}; "
            f"white-space: nowrap", f"<span>{text}</span>"))

    def zone(self, l, t, w, h, depth=2, step=8, toward="right", fill=None, line=None):
        """a repeated layer: light zone with `depth` copies behind it, offset up-right or up-left."""
        fill, line = fill or self.s["zone"], line or self.s["zone_line"]
        sx = step if toward == "right" else -step
        for i in range(depth, 0, -1):
            self.back.append(self._div(l + i * sx, t - i * step, w, h,
                             f"background: #FFFFFF; border: {self.s['stroke']}px solid {line}; border-radius: 16px"))
        self.back.append(self._div(l, t, w, h, f"background: {fill}; border: {self.s['stroke']}px solid {line}; border-radius: 16px"))

    def header_pill(self, l, t, text, text_w, pill_text, pill_w):
        """zone name + repeat pill above the zone, e.g. Encoder (x N)."""
        self.text(l, t + 4, text, w=text_w, color=self.s["label"], bold=True, align="left")
        self.pill(l + text_w + 12, t, pill_w, pill_text)

    # ---------- system / agent pieces (vocabulary A) ----------
    def _icon(self, name, px, color, sw=1.8):
        return (f'<svg width="{px}" height="{px}" viewBox="0 0 24 24" aria-hidden="true" style="flex: none; fill: none; stroke: {color}; '
                f'stroke-width: {sw}; stroke-linecap: round; stroke-linejoin: round">{ICONS[name]}</svg>')

    def icon_card(self, l, t, w, h, title, icon, kind="neutral", dashed=False, chips=None, side=False):
        """module card with a stroke icon above the title (side=True: icon on the left, for narrow rows).
        chips = [(text, kind), ...] adds a row of small example chips under the title."""
        fill, stroke, color = self.s[kind]
        row = ""
        if chips:
            row = '<div style="display: flex; gap: 6px">' + "".join(self._chip_html(tx, k) for tx, k in chips) + "</div>"
        flow = "flex-direction: row; gap: 10px" if side else "flex-direction: column; gap: 7px"
        self.shapes.append(self._div(l, t, w, h,
            f"padding: 8px 8px; display: flex; {flow}; align-items: center; justify-content: center; text-align: "
            f"{'left' if side else 'center'}; background: {fill}; border: {self.s['stroke']}px {'dashed' if dashed else 'solid'} {stroke}; "
            f"border-radius: 12px; font-size: {self.f}px; line-height: {round(self.f * 1.18)}px; font-weight: 700; color: {color}; "
            f"white-space: nowrap", f"{self._icon(icon, round(self.f * 1.4), color)}<span>{title}</span>{row}"))

    def _chip_html(self, text, kind="neutral"):
        fill, stroke, color = self.s[kind]
        return (f'<span style="display: inline-flex; align-items: center; justify-content: center; height: {round(self.f * 1.45)}px; '
                f'box-sizing: border-box; padding: 0 9px; background: #FFFFFF; border: {self.s["stroke"]}px solid {stroke}; '
                f'border-radius: 7px; font-size: {self.f}px; font-weight: 400; color: {color}">{text}</span>')

    def chip(self, l, t, w, text, kind="neutral"):
        """free-standing chip: a short role, example value or size."""
        fill, stroke, color = self.s[kind]
        self.labels.append(self._div(l, t, w, round(self.f * 1.45),
            f"display: flex; align-items: center; justify-content: center; background: #FFFFFF; border: {self.s['stroke']}px solid "
            f"{stroke}; border-radius: 7px; font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; color: {color}; "
            f"white-space: nowrap", f"<span>{text}</span>"))

    def badge(self, cx, cy, label, icon="user", d=52):
        """system input / output end point: round icon badge with a bold label under it."""
        self.shapes.append(self._div(cx - d // 2, cy - d // 2, d, d,
            f"display: flex; align-items: center; justify-content: center; background: #FFFFFF; border: {self.s['stroke']}px solid "
            f"{self.s['ink']}; border-radius: 50%", self._icon(icon, round(d * 0.58), self.s["ink"], 2)))
        self.text(cx, cy + d // 2 + 5, label, w=d + 40, color=self.s["ink"], bold=True)

    def panel(self, l, t, w, h, header, icon="gear", kind="neutral", fill=None):
        """borderless light region with an uppercase header above it (scope of a skill, tool or stage)."""
        _, stroke, color = self.s[kind]
        self.back.append(self._div(l, t, w, h, f"background: {fill or self.s['panel']}; border: 0px solid transparent; border-radius: 16px"))
        hc = self.s["accent"] if kind in ("core", "seq") else "#4A5568"
        self.labels.append(self._div(l + 4, t - round(self.f * 1.55), None, None,
            f"display: flex; align-items: center; gap: 7px; font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; "
            f"font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: {hc}; white-space: nowrap",
            f"{self._icon(icon, round(self.f * 0.95), hc, 2)}<span>{header}</span>"))

    def bar(self, l, t, w, h, text, icon="database"):
        """shared state or resource spanning several modules: wide white bar with a grey border."""
        self.shapes.append(self._div(l, t, w, h,
            f"display: flex; align-items: center; justify-content: center; gap: 9px; background: #FFFFFF; border: {self.s['stroke']}px "
            f"solid {self.s['boundary']}; border-radius: 10px; font-size: {self.f}px; line-height: {round(self.f * 1.2)}px; "
            f"font-weight: 700; color: {self.s['label']}; white-space: nowrap",
            f"{self._icon(icon, round(self.f * 1.1), self.s['label'])}<span>{text}</span>"))

    # ---------- connectors ----------
    def arrow(self, pts, color=None, dash=None, head=True, width=None):
        """orthogonal polyline through pts; one svg per straight segment, head on the last segment only.
        End the last point 1 px short of the target edge (diagrams.md)."""
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            self._seg(x1, y1, x2, y2, head and i == len(pts) - 2, color or self.s["ink"], dash, width or self.s["line"])

    def _seg(self, x1, y1, x2, y2, head, color, dash, sw):
        assert x1 == x2 or y1 == y2, "segments must be horizontal or vertical"
        h = 4 if head else 0
        if y1 == y2:
            n, x = abs(x2 - x1), min(x1, x2)
            path = f"M 0 4 L {n - h} 4" if x2 > x1 else f"M {n} 4 L {h} 4"
            l, t, w, hh = x, y1 - 4, n, 8
        else:
            n, y = abs(y2 - y1), min(y1, y2)
            path = f"M 4 0 L 4 {n - h}" if y2 > y1 else f"M 4 {n} L 4 {h}"
            l, t, w, hh = x1 - 4, y, 8, n
        defs = mk = ""
        if head:
            self.mid += 1
            m = f"dc-arrow-head-filled-{self.mid}"
            defs = (f'<defs><marker id="{m}" orient="auto" markerWidth="5" markerHeight="5" refX="2" refY="2" overflow="visible">'
                    f'<path d="M0 0 L4 2 L0 4 Z" fill="{color}" stroke="none" style="stroke: none; fill: {color}; fill: context-stroke"/></marker></defs>')
            mk = f' marker-end="url(#{m})"'
        dsh = f" stroke-dasharray: {dash};" if dash else ""
        self.arrows.append(f'<svg width="{w}" height="{hh}" viewBox="0 0 {w} {hh}" preserveAspectRatio="none" style="position: absolute; '
                           f'left: {l}px; top: {t}px; width: {w}px; height: {hh}px; overflow: visible; fill: none; stroke: {color}; '
                           f'stroke-width: {sw}; stroke-linecap: round; stroke-linejoin: round;{dsh}">{defs}<path d="{path}"{mk}></path></svg>')

    # ---------- output ----------
    @staticmethod
    def _div(l, t, w, h, style, inner=""):
        size = f" width: {w}px;" + (f" height: {h}px;" if h is not None else "") if w is not None else ""
        return f'<div style="position: absolute; left: {l}px; top: {t}px;{size} box-sizing: border-box; {style}">{inner}</div>'

    def html(self, title):
        body = "\n".join(self.back + self.arrows + self.shapes + self.labels)   # paint order: zones, lines, shapes, text
        return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
</style>
</helmet>
<div style="position: relative; width: {self.w}px; height: {self.h}px; background: #FFFFFF; font-family: {self.s['font']}; color: {self.s['ink']}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{self.w},"height":{self.h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

    def save(self, path, title):
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(self.html(title), encoding="utf-8")
        return {"w": self.w, "h": self.h, "title": title}
