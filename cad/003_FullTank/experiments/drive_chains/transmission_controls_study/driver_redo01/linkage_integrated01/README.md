# Driver front clutch chain — checked development checkpoint

[Native assembly](PowertrainControlRebuild.FCStd): **3,498 physical occurrences /
615 definitions / 419 assembly groups**. It adds23 components to the preceding
[driver foundation](../mount_integrated01/README.md): four shared M784 swing links,
one M772 clutch lever, complete M789B/M576 rods, and four complete clevis, pin,
cotter and nut sets. Existing rear/center controls remain fixed.

Only the two driver side-plate definitions, two scoped floor definitions and36
foundation occurrence frames change. Actual deeper links required revised shaft
height/station. Each floor is rebuilt from its original panel before drilling
the new four-hole pattern; obsolete mount holes are absent.

The M772 hand retains723.9mm radial reach and127mm bell-arm radius. M789B retains
320.675mm stock, with complete socket insertions at both ends. M576 is a complete
1215.608440mm inferred rod; reconcile its family length with the other four
applications as those controls are built. The three-eye M784 form is an explicit
interpretation of overlapping source lines, not a recovered manufacturing drawing.

Nominal and13mm swing-web variants each pass **251 local checks,168 context pairs
without exemptions, and69 native/STEP comparisons**. All607 undeclared inherited
definitions are preserved;98 integration checks bind tested materials, frames,
metadata and hierarchy to this full native. Fresh full rebuilding reproduces
1,877 archived BReps and170,606 persistent properties. The
[qualification receipt](qualification.json) binds the evidence and dependencies.

Five [inspected views](visual_review.json) bring progression to287:
[isometric](isometric.png), [detail](driver_detail.png),
[clutch section](clutch_section.png), [source plan](source_plan.png),
and [source side](source_side.png). Floors and rod extent are clipped only for
particular display views; the saved native retains complete solids.

The existing local plan registration is reused. The source-informed handle
leans170mm outward. A126-degree projected hand/bell angle gives a47.8465-degree
hand elevation,13.5145mm nominal clearance to the sloping nose, and11.4791px
plan-tip discrepancy. More source-like122/124-degree trials hit the actual nose;
the bounded angle probe and rejected solids are retained. This is a documented
static compromise, not validation of the historical neutral pose. Shaft anchors
and handle picks are construction evidence, not independent holdouts.

Driver station/height, seat-plate form and full seat attachment remain provisional.
Next build actual M760 suspension links and M762/M763 low toggles, then close two
source-length M574 rods. Continue selectors, high/reverse operating controls,
M789A rods, brake interconnection, axial spacing and spring anchors. SNL explicitly
assigns M576 to five applications; reverse has separate M571 pipe stock, so there
are eight front long connections in total. Standard tank011 is unchanged.

Recovery:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py --candidate cad/003_FullTank/experiments/drive_chains/transmission_controls_study/driver_redo01/linkage_integrated01
```

Rebuild nominal with `trial_driver_control_linkage_v4.py` and
`../linkage_controls06.json`; part helpers are `driver_control_linkage_parts_v3.py`
and `driver_control_mount_parts.py`. Use the headless launcher with absolute
paths and a fresh output directory. Run extraction, local/context/STEP checks,
fresh reproduction and visual review before `build_driver_control_linkage.py`.
This is a reproducible static development increment, not a completed driver
station, motion qualification or finished tank.
