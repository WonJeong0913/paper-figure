# Drawing boards

A board is one HTML file per figure: a fixed-size root and absolutely positioned elements. The same file
works on a Claude Design canvas and as a plain file on disk.

## Without a Claude Design canvas

You do not need the canvas. `scripts/dc_board.py` writes the board, and `scripts/figure_audit.py` and
`scripts/dc_export.py` render it with headless Chromium. Work in a folder shaped like this:

```
<root>/project/canvas.json     # {"boards": {"Main.dc.html": {"w": 1584, "h": 370, ...}}, "order": [...]}
<root>/project/Main.dc.html
```

Each `examples/*/gen_fig.py` writes both files. Look at the figure through the PNG that the audit
(`--png`) or the export produces. The author can still edit the HTML by hand.

## On a Claude Design canvas

- One canvas per paper, one board per figure: `Main.dc.html` (Fig. 1), `Fig2.dc.html`, and so on. Give
  each board a title such as "Fig. 2 — Query Planning & Retrieval". Put candidates and new versions to the
  right of the original (`Fig2_v2.dc.html`).
- If a canvas exists, do not create another. Read the file list, `project/canvas.json` and the boards you
  will change first. Follow the canvas type's own format instructions.
- Publish only the files you changed. Send `canvas.json` only when you add a board or change a size. If a
  publish is refused because the author edited meanwhile, re-read that file and redo the edit.
- Tell the author what changed on the canvas, not how.

## Board rules (both cases)

- The board has a fixed size: 1584 px wide for a full-width figure, 1296 px for NeurIPS and ICLR (see
  `venues.md`), so text px maps straight to printed pt. Keep the height as small as the content allows:
  figure height costs page space.
- The root is `position: relative` with px `width` and `height`. Every element inside is
  `position: absolute` with px `left` and `top`.
- **Do not draw the whole figure as one `<svg>`.** The author could not move or edit a single box. A
  non-rectangular shape is one small SVG plus a label div.
- File order is paint order: background regions and boundaries → arrows → shapes → text.
- **Arrows**: one small `<svg>` per straight segment. A bent arrow chains segments, with the head on the
  last one only. End 1 px short of the target edge. Use horizontal and vertical segments only, and never
  cross a shape. Feedback loops run in an outer band. Diagonal guide lines (zoom lines) use `line()`.
- **Labels**: each in its own div, with a width that fits the text, at least 8 px from lines and shapes.
- Write every value literally. Do not use template holes or loop tags: the export renders the markup
  without the canvas runtime.
- Decide coordinates on a grid before writing: centre a row vertically, centre a column horizontally, and
  leave 48 px or more between shapes (label width + 16 px where a label sits between them).

## dc_board.py

Write one short generator per figure (`gen_figN.py`) and keep it; coordinates are then easy to recompute
when the author asks for a change.

| Call | Draws |
|---|---|
| `card` | rounded rectangle (module, sequence transform) |
| `icon_card` | module card with a stroke icon; optional chips; `side=True` for narrow rows |
| `panel`, `bar`, `badge`, `chip` | scope panel with header, shared-state bar, user badge, example chip |
| `trap`, `trap_up` | trapezoid projection, left-to-right or bottom-up (`depth` stacks copies) |
| `op` | elementwise-operation circle |
| `cells` | tensor or vector cells |
| `tag` | parameter or external resource |
| `region`, `zone` | light region, dashed boundary, stacked ×N layer zone |
| `stack` + `bracket` | repetition |
| `arrow` | orthogonal polyline |
| `line`, `dot` | guide line, branch point |
| `math`, `text`, `panel_label`, `header`, `pill`, `header_pill` | text elements |

## TikZ

Set node sizes explicitly (`minimum width`, `minimum height`, `text width` with `align=center`). With three
or more nodes, add a coordinate map as a comment. Use `scale=` only together with `transform shape`. Place
labels with direction keywords (`above`, `below`). Set text in the pt sizes from `venues.md`.
