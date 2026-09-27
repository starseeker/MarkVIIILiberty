# Coupled driver and bow layout study — 27 September 2026

**Mechanically feasible prototype; historical position unresolved. Not integrated.**
The accepted operating-controls development and standard tank011 remain unchanged.
This study tests the complete driver mechanism against the revised bow and floor,
including actual support feet and full mounting hardware.

- [Native assembly](trial01/ControlRebuildTrial.FCStd): 189 occurrences, 81 definitions.
- [Installed STEP](trial01/exchange01/RebuiltControlAdditionsInstalled.step).
- [Transparent local isometric](trial01/visual02/isometric.png).
- [Unchanged source-section comparison](trial01/visual02/section_comparison.png).
- [Support mounting detail](trial01/visual02/mounting_detail.png).
- [Source decisions and limits](source_review.json).

## Construction and results

Main-shaft Z975 mm is a feasible sample, **not a measured historical dimension**.
Complete 49½-inch M574 stock plus the existing fork offsets determines its
X7627.311900 mm station. The swing shaft is X7220.781516/Z995 mm. Seventy-two
internal driver occurrences translate together by (+47.418492, 0, −325) mm;
their definitions, relative arrangement and control state are preserved.
Five long front rods and their forty joint parts turn to the fixed receiving
eyes. M574 and the printed M789A/M789B short stock remain complete. Three M576
applications share one unprinted 1298.292819 mm rod definition; two other
applications remain to be built.

The preceding task note incorrectly called M575/M578/M573 rear rods missing.
They are already installed in the accepted development and remain fixed context.
The earlier support mounting points stand 211–222 mm above the corrected floor.
The new estimated 6.35 mm support feet follow both actual floor planes; eight
complete mounting stacks seat on real surfaces through eight new receiving holes.
All forty bow-study plates retain their material and frames except those holes.
Support outlines, sharp bends and mounting details remain approximations.

Both nominal Z975 and variation Z970 pass:

- 521 saved-material, frame, full-stock, receiving-bore and contact checks.
- 1,022 nearby material-intersection pairs against each other and all retained
  development/standard context, with no findings and no mating exemptions.
- 226 strict STEP comparisons: 43 new/revised definitions and 183 installed parts.

The complete handles clear the bow by 8.898 mm nominal and 11.288 mm in the
variation. A fresh nominal rebuild reproduces all 243 archived BReps, all frames,
all stable persistent properties and source metadata. No relaxed mass-convergence
criteria, shortened stock or collision-shaped cuts are used.

## Historical limitations and visual review

The section comparison visibly places the shaft below the depicted source joint.
The unchanged local SNL6 registration also retains the earlier 47–49 px grip
discrepancy. The source control state, 37-inch handle datum and whole-figure scale
transfer remain open. Thus these passing mechanical checks **do not select Z975
as the correct tank layout**. The HB35 inclusive enclosure-length interpretation,
bow/floor plate boundaries and floor allocation remain conditional as before.

All three visual02 images were inspected. The isometric omits three long rear
roof panels for visibility only; the mounting view crops only its displayed floor
copies to its labeled window. Every physical part is retained in native/context
checks. These diagnostic views do not advance accepted progression beyond 308.

Next reconstruct the M791 adjustable seat evidence, four SH289E bearings, two
SH291X clips, M788 angles and the complete M786/M787 support extensions. Use SNL2
and HB6 to constrain the coupled shaft/seat layout before integrating a correction.
Do not refit a camera simply to remove the current disagreement.

## Reproduce and verify

Use the headless launcher with absolute worker/output paths and fresh runtime
directories. Run `build_driver_bow_layout.py --output PATH --main-z 975`, extract
with `pump_integration_worker.py`, then run `check_driver_bow_layout.py`,
`check_control_rebuild_context.py`, `exchange_control_rebuild_clutch_swing.py`, and
`render_driver_bow_layout_v2.py` on the saved candidate. Repeat at Z970 for the
variation. A second nominal run is compared by
`check_control_rebuild_reproduction.py`. Parameters require regeneration; this is
not a live-expression model. Prototype grouping is local and must be explicitly
mapped into the tank hierarchy before any future integration.

The frozen study, exact workers, inputs and results are checked with:

```bash
python3 cad/003_FullTank/experiments/drive_chains/verify_driver_layout_study.py
```
