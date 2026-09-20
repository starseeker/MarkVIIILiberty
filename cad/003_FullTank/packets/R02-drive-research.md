# R02 — drive interface preparation

Research only, 20 September 2026. No drive-wheel geometry or source lock is
changed by this note. The existing drive/idler annuli remain layout geometry.

HB132 describes the 3-inch-pitch, 50-pitch drive chain, the 23-tooth central
chain sprocket and the roller pinions at its sides. HB133 then explicitly says
those roller pinions mesh with the road-track driving wheel. The latter's
39.237-inch diameter, 35 teeth, 3.735-inch pitch and 2-inch tooth width describe
that toothed-wheel assembly. The HB119 9:37 reduction remains a separate count
conflict. HB137's 11.154-inch road-track pin pitch is a different interface
control: do not silently make it equal to the 3.735-inch gear pitch or assume
that a conventional one-tooth-per-track-pin sprocket is established.

Inspected HB Plate83. It shows two tooth rings, separate outer disks/bosses and
rivet rows, with deeply relieved diaphragm/web pieces between them. The roller
pinion is visible behind the wheel. A filled annular cylinder does not reproduce
this topology. The next physical reconstruction should retain the separately
identified M1401 teeth, M1403 bosses, M1404 disks and M1405 diaphragms, plus the
shaft/bushing, bearings, keys, nuts and oil fittings. Source quantities and any
production substitutions must be reconciled before repetition.

HB134 prints a 27.625-inch-long, 4.434-inch-diameter drive-wheel shaft, and a
5.118-inch-diameter, 8-inch-long bronze bushing described as interchangeable with
the roller-pinion bushing. Its removal sequence separates the outer bearing,
shaft, wheel and floating bushing. These are useful printed controls and
assembly boundaries even while the tooth/track engagement remains unresolved.

Keep three interfaces distinct during modeling: final-drive chain to central
sprocket, roller pinions to the road-wheel tooth rings, and road wheel to the
road-track links. Inspect the wheel/link transverse and longitudinal sections
before defining an actual track-driving contact contour. This note does not
resolve the 35/37 count, the reference circle of the 3.735-inch pitch or the
printed outside-diameter consistency.

The inspected image below must join the authored source lock if new geometry
consumes it; this preparation note alone does not change the current build.

| Source | SHA-256 |
|---|---|
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate83.png` | `b872de5bce7815ded1b5e8c69da1ebc44dccbde5c546b67ae7a941b9ae0224a3` |

## Shared wheel-part constraint for the next drive reconstruction

Read-only follow-up during idler-mount qualification, 20 September 2026. The
idler envelope has since been replaced by physical parts; the drive wheel is
still layout geometry. SNL275:005–014 gives the same 119-leaf rotating-wheel
composition as the idler, replacing only the two M147/M1471 rims with two M1401
rings. The boss, disks, five X and one Y diaphragm, and all three rivet sizes
share their frozen identities. Do not duplicate or silently resize those shared
parts when adding the drives. The present disk radius and rim-joint geometry
are inferred from the idler; they must be checked against the toothed ring and
roller-pinion clearance before shared definition reuse can be called qualified.

HB132's **23.031-inch** diameter is explicitly the central chain sprocket,
with 23 teeth. HB136's outline entry under road-track driving wheel uses that
same number; it is not independent evidence that the large M1401 road-wheel
rings should be reduced to 23.031 inches. HB133 separately prints 39.237 inches,
35 teeth and 3.735 pitch for the road-track driving wheel. These belong to the
gear/roller interface, distinct from the track's 11.154-inch pin pitch.

As a diagnostic only, 35 teeth at a **circular** pitch of 3.735 inches imply a
41.611060-inch reference diameter. Treating it as a **chord** pitch gives
41.666988 inches. Both exceed 39.237 inches; the source does not specify the
reference circle clearly enough to equate them with a physical outside diameter.
Conversely, 39.237 inches with 35 teeth gives 3.521905-inch circular spacing or
3.517178-inch chord spacing on that circle. Preserve this mismatch and the
separate HB119 9:37 ratio conflict. Do not manufacture a claim of compatible
historical gearing by choosing one number and dropping the other controls.
A static approximate tooth profile can be documented later, but drive engagement
needs an explicit reviewed interpretation and native checks against both the
roller pinions and road-track links.
