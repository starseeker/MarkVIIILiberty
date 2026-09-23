# Reconstruct from evidence without hiding uncertainty

Use full source figures and their catalogue context. Preserve document, page,
figure/callout, piece mark, configuration applicability, file hash and the literal
wording or value behind a dimension. A cropped shape can lose its leader line or
assembly context. Separate scanned wording, transcription, interpretation and
chosen approximation in the packet.

Before fitting geometry, identify the part, its installed quantity and its
interfaces. Catalogue assembly totals can include subassemblies already counted;
source quantity is not automatically the number of extra installed pieces.
Named source alternatives or later production variants need explicit selection.

When values conflict, retain the original values and calculate the consequences
of each defensible interpretation. For example, an outside diameter and assumed
wire diameter imply a spring inside diameter; a negative clearance is evidence of
a conflict, not authorization to relabel the printed dimension. A geometrically
plausible alternative remains an inference until better evidence supports it.

For source scaling, document datum/axis choices, calibrated dimension, anisotropic
scan distortion where present, pixel-pick uncertainty and held-out dimensions.
Do not transfer a longitudinal side-view calibration to a transverse section.
Reserve unprinted profiles, wall thicknesses, fastener details and fits as named
approximations with useful bounds. Keep physical fit allowance, historical
uncertainty, and numerical Boolean tolerance in separate fields.

Check the model against the evidence and its neighbors, rather than only against
the same parameter table used to build it. Review silhouettes and sections that
show the disputed feature. Track definition coverage, installed occurrence
coverage and evidence confidence separately. Record what remains unresolved and
which additional evidence could change the chosen geometry.

For MarkVIII work, use `docs/templates/cad-work-packet.md` and the source-linked
stage data. The user-selected priority is the fully populated standard assembly,
including interiors, before pose variants; that priority belongs to this project,
not to a universal FreeCAD rule.
