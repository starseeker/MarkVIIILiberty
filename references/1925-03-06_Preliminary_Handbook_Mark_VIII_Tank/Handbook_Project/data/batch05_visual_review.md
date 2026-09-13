# Batch 05 validation record

- Scribus 1.6.1 reopened the saved hundred-page master.
- All 3,579 native text frames match their expected strings, occupy one line and
  have no overflow. This batch adds 698 frames; none needed scale below 85%.
- All expected PDF text sequences are present. Four new small-cap Note lead-ins
  extract as NOTE; their explicit pdf_text values document that transformation.
- All PDF fonts are embedded; no extracted text lies outside its page.
- All 67 relative image links and SHA-256 artwork hashes resolve correctly.
- All twenty new pages were rendered at 144 dpi with Poppler and visually checked.
  Text wrapped around Plates 54/55/56/60, the rotated ten-row legend on page 95,
  two native stacked fractions and all sixteen new artwork crops were inspected.
- Text baselines were straightened within continuous runs using observed source
  spacing; source estimates remain recorded in body_batch05.json. A caption
  fragment outside the lower Plate 62 drawing was masked before final export.
  Page 95 was rendered again and inspected after that correction.
- All twenty source pages were visually inspected. Enlarged crops checked the
  fractions, part numbers and unusual readings recorded in REVIEW_NOTES.md.
- All 3,291 earlier page objects retain text, geometry and style assignments.
  Internal ItemID values regenerate during save. Two earlier scale values round,
  and three unused line SHADE attributes disappear, as listed in the report.
- All earlier eighty PDF pages are pixel-identical to checkpoint 04 at 144 dpi,
  verified again against the final export.
- The 21-page comparison includes source and reconstruction for pages 81–100.
  Its introduction and pages 89, 95 and 100 were rendered and visually inspected.
- Font identification, physical trim and independent proofreading remain open.
