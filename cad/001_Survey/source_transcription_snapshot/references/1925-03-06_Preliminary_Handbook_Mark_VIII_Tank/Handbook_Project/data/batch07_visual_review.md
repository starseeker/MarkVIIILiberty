# Checkpoint 07 visual review — printed pages 121–140

All twenty source pages and all twenty Poppler-rendered reconstructed pages were
visually inspected at 144 dpi. Contact proofs are in `proofs/checkpoint07/`.
PNG files were loaded with Pillow to detect truncated writes and repaired using
captured Poppler stdout when necessary. Revised pages were re-rendered and checked.

- Pages 121–129: all transmission artwork and native plate labels/captions checked.
  The Plate 75 label was returned to the left side to follow its source placement.
  Page 129's three-line rotated caption is native text and clear of the drawing.
- Page 122: all 64 legend rows, original reference gaps and wrapped descriptions
  checked in an enlarged source crop and native proof. No numbering inferred.
- Pages 125–126: duplicate ref. 18, the M–311 oil cap, reference letter I and the
  compact driving-member specification rows checked against the source.
- Page 127: detached OCR list numbers and the lower page continuation recovered;
  procedure hierarchy and paragraph endings reviewed.
- Pages 130 and 136: chapter openings, complete specification rows, leaders,
  bottom folios and continued body text checked. Original unusual wording and
  differing/unitless measurements retained without engineering corrections.
- Page 132: nominal half-spread crop clipped line endings. A wider x=1850 crop
  recovers them. Split OCR rows were rejoined, all binding-side wording checked,
  and text baselines regularized. The 9/16 and 7/32 stacked fractions are editable;
  the 7/32 placement was refined using its original source coordinate.
- Pages 131, 133, 137, 139 and 140: table headers, reference and part cells, native
  wrapped descriptions and clearances to following body text checked. Original
  blank references, M–1405 xy, shorter 2097–D89 and duplicated M–1472 retained.
- Pages 133–140: paragraph and page continuations, fractions, small-cap Note
  lead-ins, caption positions and all plate crops reviewed. Original drawing
  lettering stays raster. Page 140 ends with the original unfinished sentence.

The comparison PDF has 21 pages and 21 bookmarks. Its introduction and selected
rotated/table pages were rendered and checked. DejaVu Sans comparison fonts are
embedded; handbook pages use embedded C059 fonts.

All 5,544 text frames pass reopened-native validation. The cumulative PDF has
140 pages, 90 valid relative artwork links, no missing expected text sequences
and no text outside page bounds. Pages 1–120 are pixel-identical to v6 at 144 dpi.
All 5,075 earlier native page objects and named styles are unchanged, apart from
regenerated internal ItemIDs. See validation JSON for hashes and detailed checks.

Independent proofreading and confirmation of original typeface/physical trim
remain pending. Source texture and binding distortion within artwork remain;
no geometric rectification is claimed.
