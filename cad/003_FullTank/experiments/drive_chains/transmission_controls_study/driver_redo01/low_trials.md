# Low-speed receiver reconstruction and source correction

The selected prototype is `low02`, with `low_variation02` and fresh reproduction
`low_reproduction02`. Its full integration and acceptance are recorded separately
at `low_integrated01`. The M762 front selector coupling remains unfinished.

The [local source close-up](low_source_views01/hb113_joint_grid.png) separates four overlapping joints. In the saved HB113
crop/rotation, M784 uses short/long eyes at[475,408]/[468,442]; M761 is[487,386]
and M763's long-rod eye is[486,442]. The preceding clutch checkpoint conflated
some of those outlines. [Reviewed picks](low_source_landmarks01.json) replace the
incorrect identity assignments while preserving the original projection. These
are construction picks, not independent validation points.

The [layout probe](low_layout_probe01.json) compares driver heights and unprinted
clutch arm angles before rebuilding the complete prototype. Every setting retains
printed M574/M789B stock and the corrected receiving points. The selection uses
main/swing heights1300/1320mm and136-degree projected clutch arm angle. It leaves
11.4125mm nominal hand/nose clearance and10.1281px source-plan hand-tip discrepancy.
Absolute height, seat geometry and neutral pose remain unmeasured.

| Trial/check | Disposition |
|---|---|
| low01 | Rejected: M763's lateral set starts inside both joint regions, overlapping M760 by704.778mm³, the lower clevis by149.133mm³ and the pin by0.14845mm³ per side. Some initial catalogue locators were also wrong. |
| low02 geometry | Holds35mm at each end in the real joint plane and places the lateral set in the middle. Both receiver bores cut through the entire fused stock. SH220A now seats against M762, matching its listed association. |
| initial low02 checker | Rejected the intended oil opening by requiring an uninterrupted cylindrical journal area. Saved results are retained under `diagnostics/journal_area01`. |
| checker revision2 | Checks full axial journal span and compares independently reconstructed annular hub material minus the real oil passage in both material directions. No geometry or tolerance relaxation. |
| nominal /13mm suspension web | Each passes366 local checks,227 context pairs without exemptions, and105 native/STEP comparisons. Fresh prototype reproduction passes. |

SNL119 identifies two each M760/M762/M763; M761 is137:020, its3/16×1¼-inch cotter
is141:010, SH220A is272:001, and M574 is195:011. The printed49½-inch M574 dimension
is interpreted as rod stock, retaining full clevis sockets and nut coverage.

M760 hangs on the existing rear shaft; M762 and M763 share its lower pin. The
selected axial stack and pin dimensions are estimates. The curved M762 front
ends have actual open eyes but no invented selector pins. Their definitive
connection must be resolved while building the selectors. HB and SNL also differ
on M756/M757 handed names; record the selected catalogue convention explicitly.
