# Venues: width, text size, audit presets

Pass the venue to the scripts: `--venue icml`. Add `--column` when the figure sits in one column instead
of the full text width. The preset sets the printed width, the smallest (and for Nature the largest)
text size, and the thinnest line.

Printed text (pt) = text px × placed width (pt) ÷ board width (px). 1 mm = 2.835 pt.

## Presets

Widths and the rules in the "Venue states" column are taken from each venue's template or author guide.
A size marked * is this skill's default, used because the venue states no minimum.

| `--venue` | Full width / one column | Venue states | Min text | Smallest text on the board |
|---|---|---|---|---|
| `icml` | 171.5 mm (6.75 in) / 82.6 mm | caption 9 pt; lines ≥ 0.5 pt; no text on a grey background; no title inside the figure; label every component | 9 pt* (caption size) | 30 px of 1584 |
| `neurips`, `iclr` | 139.7 mm (5.5 in), single column | artwork neat, clean, legible; lines dark enough; should read in black and white | 8 pt* | 27 px of 1296 |
| `acl` (`emnlp`, `naacl`, `eacl`, `aacl`) | 160 mm / 77 mm (A4) | caption 10 pt; prefer vector graphics; do not rely on colour alone; greyscale readability strongly encouraged | 9 pt* | 32 px of 1584 |
| `aaai` | 177.2 mm (2 × 3.3 in + 0.375 in) / 83.8 mm | **figure text ≥ 9 pt**; **lines ≥ 0.5 pt**; fonts embedded, no Type 3 fonts; avoid colour (printed in greyscale) | 9 pt | 29 px of 1584 |
| `cvpr` (`iccv`, `wacv`) | 174.6 mm (6⅞ in) / 82.6 mm | resize figure fonts to match the 10 pt body text; call-outs 9 pt Helvetica; nothing may be lost in greyscale | 9 pt* (aim for 10) | 29 px of 1584 |
| `ieee` | 181.9 mm (7.16 in) / 88.9 mm (3.5 in) | do not size a graphic narrower than one column; raster art ≥ 300 dpi, line art ≥ 600 dpi | 8 pt* | 25 px of 1584 |
| `acm` | 177.9 mm / 84.8 mm (acmart `sigconf`) | every figure needs a `\Description{...}` unless it is decorative | 8 pt* | 26 px of 1584 |
| `nature` | 183 mm / 89 mm (1.5 columns: 120–136 mm); page depth 247 mm | **text 5–7 pt**, sans-serif (Helvetica or Arial); panel labels 8 pt bold upright lowercase; lines 0.25–1 pt; RGB | 5 pt, max 7 pt | 16–21 px of 1584 |

For any other venue, pass its numbers directly: `--placed-mm <text width in mm> --min-pt <smallest text>`.
Take both from the venue's template. If it states no minimum, use 8 pt. The scripts stop when they get
neither a venue nor these two numbers.

Templates change. Confirm the numbers against the venue's current author kit before submission.

## Board width

- Two-column venues: draw full-width figures on a **1584 px** board and one-column figures on a board of
  `1584 × column ÷ full width` px (about 756–775 px).
- NeurIPS and ICLR: use a **1296 px** board. It prints at the same scale as a 1584 px board at ICML
  (0.306 pt per px), so the same px sizes apply: 30 px is 9.2 pt.

## One board, different venues

1 px on a 1584 px board prints as 0.307 pt at ICML, 0.286 pt at ACL, 0.317 pt at AAAI and 0.327 pt at
Nature.

- A 30 px figure made for ICML prints at 8.6 pt at ACL: below 9 pt.
- The same figure prints at 9.8 pt at Nature: above 7 pt.

Keep the board and change only the venue for the audit and the export. Re-measure every time the venue
changes.

## Details that trip the audit

- Subscripts render at about 83 % of the text size. If that falls below the limit, set the size
  explicitly: `<sub style="font-size: 30px">`.
- Chromium floors CSS border widths to whole px: 1.6 px becomes 1 px (0.31 pt at ICML), which is under
  0.5 pt. Use 2 px borders (0.61 pt). SVG strokes are not floored.
- With `--max-pt`, single letters up to 1.5 pt above the limit pass, so 8 pt panel labels are accepted
  at Nature.
