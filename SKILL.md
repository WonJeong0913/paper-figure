---
name: paper-figure
description: Draws and fixes research-paper method, pipeline and architecture figures as editable Claude Design boards, without image-generation models. Preserves the author's structure, sizes text for the target venue (ICML, NeurIPS, ICLR, ACL, AAAI, CVPR, IEEE, ACM, Nature), compares candidates with reference figures, measures at print size, and exports vector PDF and 300 dpi PNG. Use for "make a figure", "fix Fig. 2", "overview figure", "architecture diagram", "check my figure".
---

# paper-figure

Draw a paper figure from separately placed, editable elements, then measure it at the size it will be
printed.

## Principles

- **No image-generation models.** You or the author draw every element.
- **Deliver the figure as a board on a Claude Design canvas whenever that tool is available.** This is
  required. Create or update the board first, so the author can move, restyle and comment on every
  element. Never finish with only a PNG, a PDF or a local HTML file. Draw plain HTML boards on disk only
  when the session has no canvas tool, and say so in the report (`references/drawing-boards.md`).
- **PDF and PNG are exports**, made when the author asks or the figure is final: a vector PDF with live
  text for LaTeX, and a 300 dpi PNG made from it for Word and slides.
- **Figure text uses exactly the names in the paper body**, in the language of the paper.
- **Structure is preserved.** You may change shapes and layout. You may not change modules, connections
  or boundaries without asking (see "Structure ledger").
- **Pick the target venue before drawing.** Venues disagree: Nature caps figure text at 7 pt, AAAI
  requires at least 9 pt. If the author has not chosen, pick the venue typical for their field and say so
  in the report.
- **The quality bar is a top-venue figure.** Look at reference figures first, build candidates, and let
  the author choose. Do not stop at boxes and arrows.
- **Say "passes" or "no overlap" only after measuring** with `scripts/figure_audit.py` and looking at the
  render yourself. This overrides any "do not verify" default of the drawing surface.
- **Visual critique is advisory.** It miscounts elements and misses connections. Judge structure only
  with the ledger and `--compare`.

## Workflow

1. **Read the sources**: paper draft, code, and the author's own figure. Read them again every time the
   author says "redo it".
2. **Build the structure ledger.**
3. **Write the brief and pick the venue** (`references/venues.md`).
4. **Open 2–3 reference figures** and write the style sheet.
5. **Draw 2–3 candidates** on the canvas that differ in layout or shape vocabulary, not in small tweaks.
6. **Audit, look, compare, critique.** Fix until errors are zero.
7. **Show the comparison sheet. The author chooses.**
8. **Export** once the author has chosen, place the figure in the manuscript, and look at that page.

## Structure ledger (before any edit)

A figure shows the system the author designed. Extract every item below from the author's figure, the
paper and the code into a table.

| Kind | Items | Source |
|---|---|---|
| Modules (boxes) | exact names | original figure / code path / paper section |
| Connections (arrows) | sender → receiver : data name | the code that produces that data |
| Boundaries | what each system, skill or tool encloses | original figure / code |
| State and resources | shared state, budgets, shared model, corpus, learned parameters | original figure / code |
| Decisions and loops | decision outcomes, feedback and recurrence paths | policy function / algorithm |
| Inputs and outputs | user input, final output, input and output tensors | original figure / code |

When drawing someone else's method, build the ledger from the original paper's algorithm and official
code, and cite them.

- Nothing in the ledger may disappear, be renamed, or move across a boundary. If it must change (for
  example, the figure disagrees with the code), **ask the author before editing**.
- Do not invent modules or arrows, and do not drop connections to simplify. Note deliberate omissions in
  the caption or the report.
- Layout may change. Flow direction and containment may not.
- Detail figures split the overview figure. Names, colours and boundaries must match it.
- Check every arrow against the code: it must leave the module that actually produces that data.
- After editing, check the ledger line by line and run
  `python3 scripts/figure_audit.py NEW --venue icml --compare ORIGINAL`. The script cannot see
  unlabelled arrows; check those against the ledger by hand.
- Start the report with "Structure changes: none" or the list of changes and whether the author approved.

## Working with the author

- **The author's own drawing is the baseline.** Remove and align on top of it. Do not replace its
  structure or style wholesale.
- **Never overwrite the original.** Put each new version beside it (`Fig2_v2`). The author confirms.
- If the author edited the board by hand, re-read the latest file and work on that.
- Add one kind of element at a time. Adding stage panels, pills and output boxes at once makes the figure
  too complicated.
- Keep neighbouring stages as **dashed boxes with their real names**. Do not delete them or reduce them
  to an arrow or grey text.
- Report only what changed, per figure. If you find a mismatch with the paper or code, say so before
  editing the figure.

## Brief, references, style sheet

**Brief (one per figure)**
```
Role:            overview (structure + procedure) / stage detail / architecture block
Figure type:     A system or agent pipeline / B model or architecture
Venue:           sets the placed width and the text px (references/venues.md)
Reader takeaway: one line
Facts to keep:   the structure ledger
Leave out:       result numbers, sentences that belong in the body, settings such as model names
```

**Reference figures (2–3)**
- Order of preference: the method's original paper or official repository; a recent paper at the same
  venue with the same figure type; the author's earlier figures.
- Open each one and note: shape vocabulary, what each colour means, fonts and variable notation, layout
  skeleton, amount of text, and **what not to imitate**.
- Take conventions only. Never redraw a reference figure or reproduce its palette and composition.

**Style sheet (one per paper)**
- Every figure in a paper uses one visual vocabulary: font, text px, colours and their meanings, shapes,
  line and border widths, corner radius, arrowheads.
- With `scripts/dc_board.py`, the `STYLE` dict is the style sheet. Change it there, never per element.

## Composition rules

- A box holds a **function name** only. Explanatory sentences go in the body text.
- An arrow carries a **data-name label**. Do not number data.
- No placeholder names such as A/B/C or "To B / From A". Use the real module names.
- A boundary encloses only the part that really does that work.
- Box text is keywords: no sentences, nothing over 15 words, no pasted body text, no lists of equations.
  A short data example is the exception.
- No step-number badges on stages. No title inside the figure; the title is the caption.
- An overview shows structure and procedure together: input → process → output reads left to right in a
  few seconds, feedback loops are dashed, and the output is clearly visible.
- Run **one worked example through all detail figures**, as small chips inside boxes.
- Consider merging overview and detail into panels a and b of one figure (stacked, or macro–micro zoom
  lines). Build both as candidates.
- When rules conflict, decide in this order: relations and direction match the code and paper → flow
  reads in seconds → readable at print size → alignment → looks.

Shape vocabulary, fonts, colours and lines: `references/style.md`. Pick vocabulary A (system pipelines:
icon cards, chips, panels) or B (architectures: shape says type) and do not mix them in one paper.

## Size

Printed text (pt) = text px × placed width (pt) ÷ board width (px). The same board prints at different
sizes in different venues, so re-measure whenever the venue changes. Presets and px sizes:
`references/venues.md`.

- Keep text sizes nearly uniform in a figure. Do not shrink some text to make it fit: move text to the
  caption, enlarge the box or board, break the line, or split the figure.
- Text must not leave its box or sit within 6 px of the border.
- Five or more boxes in one row run out of width: break titles into 2–3 lines, then go to two rows.
- A wide figure goes at full text width (`figure*`). In one column its text halves.
- With several panels, align rows exactly or separate them by 7 px or more.

## Audit loop

Setup: `pip install playwright numpy pillow && python3 -m playwright install chromium`
(poppler-utils enables the PDF check).

```bash
python3 scripts/figure_audit.py project/Fig2.dc.html --venue icml --png fig2.png     # measure + render
python3 scripts/figure_audit.py project/Fig2.dc.html --venue nature --column         # one-column figure
python3 scripts/figure_audit.py project/Fig2.dc.html --placed-mm 165 --min-pt 8      # venue without a preset
python3 scripts/figure_audit.py project/Fig2.dc.html --venue icml --cvd fig2         # grey + colour-blind
python3 scripts/figure_audit.py project/Fig2_v2.dc.html --venue icml --compare project/Fig2.dc.html   # labels kept?
```

1. Fix until ERROR is 0: text below or above the limits, text outside its box, overlapping text, text
   off the canvas, a label missing from the original. For each WARN (text hugging a border, text crossing
   a line, fallback glyphs, text on grey, lines under the minimum, near-miss alignment), zoom into the
   render and decide.
2. Look at the render **at placed size**, and at the three `--cvd` images.
3. Check arrows and labels against the ledger, the code and the paper again.
4. Score with the critique table and compare with the reference figures.
5. Keep the previous file each round and record only what changed.

**Fix order** (prevents rework): canvas and margins → large regions and stacking order → shape sizes →
fills and borders → connector endpoints → text → decoration.

**Done means all three**: the audit passes, you looked at placed size, and the critique clears the pass
mark. A passing audit alone is not enough. If problems remain after five rounds, the layout itself is
wrong: tell the author and decide together.

## Candidates and critique

Make 2–3 boards with the same structure and a different layout or vocabulary (panels a/b versus zoom
lines, left-to-right versus bottom-up, vocabulary A versus B). Stack the candidates and the reference
figures into one image and show it:

```python
from PIL import Image
ims = [Image.open(p).convert("RGB") for p in ["vA.png", "vB.png", "ref.png"]]
W = 1584; ims = [im.resize((W, round(im.size[1] * W / im.size[0]))) for im in ims]
sheet = Image.new("RGB", (W, sum(im.size[1] + 30 for im in ims)), "white"); y = 0
for im in ims: sheet.paste(im, (0, y)); y += im.size[1] + 30
sheet.save("compare_sheet.png")
```

Score each dimension 0–2.5 (total 10). Any veto sets that dimension to 0.

| Dimension | Meaning | Veto |
|---|---|---|
| Faithfulness | shows the method within the caption's scope; reasonable simplification is fine | invented module or connection, reversed flow, missing required connection, out of scope, broken text or fake formulas |
| Conciseness | a visual summary with high signal to noise | sentences in boxes (over 15 words), pasted body text, equation lists |
| Readability | flow at a glance, legible text | title or caption inside the figure, redundant labels, overlaps, tiny or uneven text, tangled flow |
| Aesthetics | top-venue polish | grid artefacts, broken shapes, neon or clashing colours, clip art, mixed fonts, misalignment, black background |

Pass marks: journal 8.5, conference 8.0, thesis 8.0, poster 7.0, slides 6.5. For each dimension also
write "better / equal / worse than the reference" with one line of reasoning.

## Export

```bash
python3 scripts/dc_export.py <root> Fig2.dc.html --out paperfigs --venue icml
```

- Writes `Fig2.pdf` (vector, board size) and `Fig2.png` (300 dpi at the placed width).
- The PDF check must pass: **all fonts embedded, no Type 3 fonts, no raster images**. If it fails, fix
  the font list first (`references/style.md`).
- LaTeX: `\includegraphics[width=\textwidth]{figures/fig2.pdf}` inside `figure*`. Do not shrink with
  `\resizebox` or `scale=`. One-column figures use `figure` and `\columnwidth`.
- Word and slides: insert the PNG at the figure width, then check that page for overlaps and page
  breaks.
- Back up the previous figure before replacing it in the manuscript, and replace only after the author
  decides.
- Captions follow the venue template. State in the caption what example symbols mean, what was left out
  on purpose, and that an example is illustrative.

## Never

- Add, remove or rename a module, connection or boundary without the author's confirmation.
- Use an image-generation model, deliver a bitmap-only final figure, or copy a reference figure.
- Finish with only a PNG, a PDF or a local file when a canvas tool is available.
- Put result numbers in a method figure, or vary colour rules, text size or vocabulary between figures
  of one paper.
- Put text on grey, use fractional-px CSS borders, or ship a PDF with Type 3 fonts.
- Overwrite the author's original, swap a figure in the manuscript unasked, or pick the candidate for
  the author.
- Claim "readable" or "no overlap" without measuring.

## Files

| File | Use |
|---|---|
| `scripts/dc_board.py` | builds boards from short Python: cards, icon cards, trapezoids, operation circles, tensors, panels, arrows |
| `scripts/figure_audit.py` | measures a figure at print size; `--venue`, `--compare`, `--cvd` |
| `scripts/dc_export.py` | board → vector PDF + 300 dpi PNG, with PDF font and raster checks |
| `references/venues.md` | venue presets: widths, stated rules, smallest text in px |
| `references/style.md` | shape vocabularies A and B, fonts, colours, lines, density |
| `references/drawing-boards.md` | drawing on a Claude Design canvas or as plain HTML boards; `dc_board.py` calls; TikZ notes |
| `references/credits.md` | sources of the borrowed procedures and their licences |
| `examples/` | runnable figures that pass the audit: `react-agent` (vocabulary A), `transformer-block` (vocabulary B), `rag-pipeline` (minimal) |
