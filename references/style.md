# Style: shape vocabulary, fonts, colours, lines

Choose one vocabulary per paper. Do not mix them.

## A. System, agent and LLM pipelines

- **Card**: a 28 px stroke icon on top, a bold title below, optional regular-weight detail in the same
  span. Corner radius 12 px. Neutral modules are white with a `#5B6472` border. Key modules get a light
  fill (for example `#F3F1FE` with a `#7F77DD` border).
- **Chip**: a short role, example or size inside a card (`E1`, `Δ(x)`, `D→2ED`). Radius 7 px. Draw arrow
  symbols as small SVG paths, not as text glyphs.
- **Panel**: a borderless light region (radius 16 px) with an uppercase header above it (bold, 1.2 px
  letter spacing, small icon).
- **Repetition**: stacked copies of a card behind it, plus a bracket and a pill (`×N per query`).
- **External resource or parameter**: a white tag with a grey border, joined by a dashed arrow.
- **Neighbouring stage**: a dashed card with its real name and the icon on the left.
- **System boundary**: `2px dashed #9A988F`, radius 18 px. System input and output end in a 48 px round
  badge icon (for example a user).

## B. Models and architectures (shape says type)

- **Trapezoid = linear projection.** The wide side is the higher dimension.
- **Rounded rectangle = sequence transform** (SSM, convolution, attention, scan). Only the paper's key
  module gets the emphasis fill.
- **Circle = elementwise operation** (σ, ×, +, N), symbol in serif. Explain symbols in a small legend or
  the caption.
- **Stacked cells = tensor or vector. Cylinder = store, buffer or memory. White tag = learned parameter or
  external resource.**
- **Variables sit on the lines in serif italic** (x, z, y, Δ, hₜ). Do not put them inside boxes.
- **Layer stacks at 9 pt or more**: put each sub-layer card beside the residual trunk and the Add & Norm
  (or ⊕) on the trunk at the same height (ladder layout). It is about 35 % shorter per layer than routing
  a bypass around a card on the trunk. Keep the normalisation position (post-LN or pre-LN) as in the
  original paper.

## Fonts

- Labels use one sans-serif family: bold for module names, regular for details.
- **List a TrueType font first**: `Arial, 'Liberation Sans', 'Helvetica Neue', sans-serif`. If the first
  font is missing and the fallback is an OTF/CFF font such as Inter, Chromium embeds it in the PDF as a
  **Type 3 font**. AAAI forbids Type 3 fonts and other venues reject them.
- Variables: ML venues (ICML, ACL, NeurIPS) use **serif italic** to match the equations
  (`'Times New Roman', 'Liberation Serif', serif`). Nature uses sans-serif only.

## Colour

- Tie each colour to one meaning and use three or four at most. Regions get a light fill (10–15 %);
  strong colour is for the key path only.
- **Colour is never the only cue.** Pair it with lightness, dashes or weight. Pick distinguishing colours
  from the Okabe–Ito set (`#E69F00` `#56B4E9` `#009E73` `#0072B2` `#D55E00` `#CC79A7`). Do not place red
  and green of equal lightness side by side.
- **No text on a grey background** (ICML). Tags and resources are white with a grey border. No black
  backgrounds.
- A working palette: ink `#2C2C2A`, label `#3D3D3A`, neutral border `#5B6472`, key module
  `#7F77DD` / `#F3F1FE` / `#26215C`, selection path `#534AB7`, projection `#4A6FA5` / `#EAF1F8`,
  feedback loop `#D55E00` dashed, boundary `#9A988F`.

## Lines

- Lines and borders print at **0.5 pt or more** (ICML and AAAI state this; Nature asks for 0.25–1 pt).
  On a 1584 px board that is a 2 px CSS border (about 0.6 pt). See the border-flooring note in
  `venues.md`.
- Solid = main flow. Dashed = secondary flow (loops, optional or selection paths). One meaning, one line
  style. Arrowheads are small, plain and all the same size.

## Density

- With small text (7 pt or less, for example Nature), the full vocabulary A fits.
- At 9 pt or more (ICML, ACL), cut icons, chips and legends, let shape carry the meaning (vocabulary B),
  and move sizes and symbol explanations to the caption.

## What looks amateur

Default slide-deck blue and orange with heavy black borders, mixed fonts, mixed 2D and 3D, saturated
backgrounds, the same line style for data flow and auxiliary flow, neon colours, black backgrounds, clip
art and speech bubbles, visible grid artefacts, a title inside the figure.
