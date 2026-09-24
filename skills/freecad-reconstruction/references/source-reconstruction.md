# Reconstruct from evidence without hiding uncertainty

Use full source figures and their catalogue context. Preserve document, page,
figure/callout, piece mark, configuration applicability, file hash and the literal
wording or value behind a dimension. A cropped shape can lose its leader line or
assembly context. Separate scanned wording, transcription, interpretation and
chosen approximation in the packet.

Search the local figure index by component and mounting name before settling an
uncertain visible form from a general assembly view. In the Liberty gear work,
the timing section left the starting claw ambiguous; the separately indexed
exploded mounting view resolved a broad rim and larger centre opening. Numerical
geometry checks had passed the earlier hypothesis. Preserve that diagnostic and
revise the source comparison before accepting the part. The
[gear reconstruction packet](../../../cad/003_FullTank/packets/P01-engine-driving-gear.md)
records this example and its retained uncertainty.

Before fitting geometry, identify the part, its installed quantity and its
interfaces. Catalogue assembly totals can include subassemblies already counted;
source quantity is not automatically the number of extra installed pieces.
Named source alternatives or later production variants need explicit selection.

Translate explicit assembly and service instructions into geometric requirements
before finalizing estimated interfaces. A shaft can fit its bearing while an
integral gear cannot pass through the bearing housing's receiving lug. Check the
complete moving unit and the stated removal sequence; an offset access opening
does not by itself imply a coaxial path. Preserve a failed envelope as evidence,
and distinguish component fit from a verified installation or removal path. The
[lower distribution-drive study](../../../cad/003_FullTank/packets/P01-engine-lower-distribution.md)
records this constraint and the remaining casing-access work.

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

Classify each view before comparing geometry: photographic perspective,
orthographic/axonometric, explicitly oblique, or schematic/mixed. An apparent
profile disagreement can be a projection mismatch. Fit a camera only to reviewed
landmark identities and saved CAD coordinates, and retain independent holdouts.
Planar landmarks alone cannot establish an unconstrained general camera. A low
fit residual does not prove either the camera or estimated geometry is correct.

Version image bytes/crop, fitting picks, anchor coordinates, projection assumptions
and solver settings. New unrelated geometry normally reuses that camera. Changed
anchor definitions require locator review; new holdout contradictions trigger
diagnosis before any refit. Keep the old fit and a reason for changing it. Do not
silently turn failed holdouts into fitting points. The MarkVIII source-camera
controls exercise fixed-camera reuse, native-frame binding and perspective depth;
they are synthetic controls, not historical calibration evidence. Mesh previews
still require separate native-solid and interface qualification.

Check the model against the evidence and its neighbors, rather than only against
the same parameter table used to build it. Review silhouettes and sections that
show the disputed feature. Track definition coverage, installed occurrence
coverage and evidence confidence separately. Record what remains unresolved and
which additional evidence could change the chosen geometry.

For MarkVIII work, use `docs/templates/cad-work-packet.md` and the source-linked
stage data. The user-selected priority is the fully populated standard assembly,
including interiors, before pose variants; that priority belongs to this project,
not to a universal FreeCAD rule.
