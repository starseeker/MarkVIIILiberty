# X01 / I04 — roof louver geometry preparation

Preparation from the locked handbook/SNL records, 20 September 2026. The subsequent [implementation packet](X01-louvers.md) records the partial
blade/frame population in H01's inlet/outlet apertures.
Their external blades, frames and deflectors can be populated under X01 before
the complete internal cooling-system reconstruction in I04.

HB40 prints openings 946.15 mm wide, inlet 655.955 mm long and outlet 955.675 mm
long. Those values already control H01. It describes 6 mm armor blades bent
90 degrees, outside width 63.5 mm, bend radius 12.7 mm, arranged face-to-face.
The radius's inside/center/outside reference is not explicit in this text.
HB41 describes 6 mm flanged guards projecting 222.25 mm above the roof on each
side of the louver. SNL7 and SNL4 show the exterior arrangement; their oblique
images are qualitative and must not be treated as orthographic measurements.

## Quantity conflicts to resolve explicitly

| Source scope | Inlet blades M987 | Outlet blades M994 | Distance pieces M997 |
|---|---:|---:|---|
| HB40 prose | 34 | 29 | 122 combined |
| HB233/235 nomenclature | 39 | 29 | 66 inlet + 56 outlet = 122 |
| SNL18:015–016 and SNL133:016 | 34 | 28 | 68 inlet + 54 outlet = 122 |

The survey already preserves the handbook discrepancy as `HB_ERRATA_25`.
The same combined distance-piece total does not establish the allocation or the
blade count. Original HB40/233/235 and SNL18/133 scans were inspected after this table was
compiled and confirm these differing figures. Reconcile the actual edge/end-
packing topology before selecting a configuration count. Do not silently
turn an end packing plate into an extra blade or apply a single pitch to both
stacks merely to make the totals fit. A later-SNL working choice, if used, must
retain the earlier alternatives and their source scope.

## Identified component families

Inlet: M982/M983 side frames, M984/M985 end pieces, M986 cover, M987 blades,
M995A and the printed `995B` retaining plates, M1005 packing strip. The missing
M prefix on `995B` is already recorded as `SNL_ERRATA_23`; resolve through the
survey identifiers, not an invented normalized mark.

Outlet: M989 port frame plate, M990 starboard deflector-side channel, M991/M992
end pieces, M993 cover and M994 blades. M2108 is the left deflector-side channel,
distinct from M989. Each deflector channel assembly lists two M1004 fishplates;
both rows also print '(2)', so per-assembly versus whole-vehicle scope needs
inspection rather than simply summing the parenthetical figures. Rear deflector
channels are M2110/M2111.

Shared: M997 distance pieces (122 listed), M998 end packings (4), M999 frame
securing pieces (8), M1000 packing plates (4), M996 saddles (4), M988 outlet
retaining pieces (2), plus clamps, set screws and assembly hardware. Parent
assemblies on SNL133 provide explicit composition rather than extra physical
leaves. SNL151:007–011 gives the left outlet side assembly with two M1000 plates,
M993 cover and M989 side plate.

## Integration constraints

Reuse the current sloping engine-roof plane and aperture stations; distinguish
longitudinal projected opening length from true sloping length when placing
blades. Derive a representative bent plate and end/spacing stack first. Check its
normal thickness, corner-radius interpretation, air passages, neighboring blade
clearance and frame contact before repetition. Printed width/count do not by
themselves establish orientation, pitch or end clearances.

The nominal guards must be checked against both physical tracks and the rear
upper enclosure. Current hull roof strips are incomplete, so guard attachments
and the aperture frames must be modeled explicitly rather than fused into the
existing roof. Preserve the independent source overlay and save the next standard
isometric milestone when the installed roof equipment has been inspected.

## Original scan inspection

Direct inspection confirms that the count differences above are printed in the
sources. HB40 also prints the unusual 1.825-inch inlet-length remainder literally.
These five supplemental scans are recorded here and were added to the authored
source lock when promoting the louver geometry inputs.

| Source | SHA-256 |
|---|---|
| `references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p018.jpg` | `1bd4732bae2d179e9bc77e58f87a8231289f26d7cc3abbeea1a8adeb846b4ae3` |
| `references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p133.jpg` | `6f9890bc76bb4bfebfe15723982f9ade091700aa68fb7496156500c8e712cc5c` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII021.jpg` | `488786ec0dbc01be014080be0e114c3d195d835ef165e4dbc260c82005a17891` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII117.jpg` | `9fe85d6016288e0ed57c01c9c15a5a3744161773c3f6c78ee590af9ef84279af` |
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII118.jpg` | `c580d3360cee7034eaf26ac08f2f82bc75fb049ed211937390a327668a4eb059` |
