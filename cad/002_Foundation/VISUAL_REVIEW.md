# Pilot visual review — 19 September 2026

Reviewed the generated isometric, side, front, top, running-gear and joint views,
and the Plate 2 and Plate 29 calibration overlays. Compared them with the actual
SNL Plates 1–4, 10, 26 and 29 and handbook Plates 84 and 91. This is a bounded
review of the foundation pilot, not certification of a complete reconstruction.

## Findings and dispositions

| Subject | Finding | Disposition |
|---|---|---|
| Overall profile | The blockout retains the long sloping rear, raised forward track path, stepped upper enclosure and outlook shown in Plate 2. | Accepted as a coarse placement reference. The polygonal nose/tail and uninterrupted hull volume must be replaced with actual plate structure later. |
| Plan/front shapes | Width and sponson projection remain broadly consistent with the documented envelope. The photographed views do not establish an orthographic plan or complete cross-section. | Rectangular enclosure widths and trapezoidal sponsons remain provisional. No photographed perspective has been forced into a metric orthographic view. |
| Track guides | The authored closed outline follows the foldout's broad track route, with straight segments substituting for local curves. | Guide only; neither length closure nor all 78 shoes per side has been solved. |
| Shoe/link segment | Width, pitch and repeated arrangement are supported. The real shoes show pressing curvature, rivets and complex double-link/end-eye detail absent from the pilot. | Retain the visibly simplified formed plate and link webs. Do not interpret these as production-complete track-link parts or articulated joints. |
| Roller unit | Two waisted rollers, the common tube, and end retaining rings follow the handbook section arrangement. Printed diameter/width/tube dimensions control the solid. | Linear waist transitions approximate the original curved groove. Fits, ring convention and tube grooves remain explicit assumptions. The supporting shaft and suspension kit are not included. |
| Roller/rail contact | Each detailed roller contacts the top of its corresponding central-shoe rail. | Confirmed geometrically in the contact report. No force, wear or motion behavior is established. |
| Support joint | The local L section, adjacent plate and two illustrative fasteners form a coherent coupon. Plate 91 establishes this general construction relationship. | Full M2078 sweep, section size and original hole pattern remain unresolved; the coupon is not a faithful complete M2078 replacement. |
| Rendering | An initial mean-depth triangle preview obscured small foreground parts incorrectly. | Replaced with per-pixel depth rendering, then re-inspected. Native solids were unchanged. Exact TechDraw projections are also exported. |

The native assembly uses translucent reference envelopes; shaded PNG previews
use opaque faces with reference outlines, so interior pilot items can be obscured
in whole-vehicle views. Use the dedicated running-gear and joint previews, or hide
`ReferenceGeometry` in FreeCAD, to inspect the physical parts.

## Independent calibration checks

| Check | Residual | Point-picking allowance | Interpretation |
|---|---:|---:|---|
| Plate 2 drive-wheel diameter | +15.92 mm | ±36.16 mm | Within the coarse image-picking allowance; not a high-precision measurement. |
| Plate 2 idler diameter | −7.02 mm | ±35.57 mm | Rim partly obscured; same limitation. |
| Plate 29 roller width | +13.03 mm | ±3.32 mm | Disagreement remains open; use the handbook's printed 4⅞-inch width in the part. |
| Plate 29 tube length | +0.21 mm | ±3.32 mm | Consistent at the scan's limited precision. |

These checks are independent of their respective fitting spans. They do not
validate every interior feature or the transfer between preliminary, production
and service configurations. Review and update this document when changing the
authored profiles, calibration points or represented configuration.

## Verification record

The final `build` and `validate` commands completed successfully. Their generated
reports record 32 valid physical solid occurrences, no unintended positive-volume
overlaps, 23 contact pairs, relocated native links, equivalent independent
geometry rebuilds, parameter propagation, and STEP shape/hierarchy round trips.
The frozen survey's 27 original checks also passed on a disposable copy. Required
source hashes were verified again after validation.

This milestone establishes the workflow and representative geometry. Visible
plate seams, rivet patterns, complete running gear, curved link forms, production
panel details and proprietary machinery remain future work, with uncertainty
preserved in the authored issue records.
