# Space Grotesk (subset)

Used by `lab1_path_svg.py` to measure text and to embed the typeface in the
generated SVGs, so the files render identically anywhere.

- `SpaceGrotesk-Regular.ttf`, `SpaceGrotesk-Bold.ttf` — for text measurement
  and for PNG export. Converted from the woff2 files beside them (weights 500
  and 700), with the family name normalised to "Space Grotesk".
- `space-grotesk-latin-500-normal.woff2`, `space-grotesk-latin-700-normal.woff2`
  — embedded as base64 in each SVG.

Source: the `@fontsource/space-grotesk` npm package (v5.3.0).
Licence: SIL Open Font License 1.1 — https://github.com/floriankarsten/space-grotesk
