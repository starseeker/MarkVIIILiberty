# R02 — idler and shared wheel construction preparation

Research only, 20 September 2026, while upper-support qualification runs. No
idler geometry, placement or source lock is changed by this note.

## Printed controls and assembly boundaries

HB138 gives an untoothed adjusting-wheel diameter of 40.187 inches
(1020.7498 mm). HB139 says its floating bronze bushing is interchangeable with
the driving-wheel and roller-sprocket bushings. HB134 supplies 5.118-inch bushing
diameter and 8-inch length for the drive assembly; the exact diameter reference
and transfer need explicit review. Do not automatically transfer every drive
shaft dimension to the idler shaft.

HB138 gives each tension screw as 15⅜ inches long (390.525 mm), 1⅞ inches in
diameter (47.625 mm), nickel steel, in a cast-steel bracket. Two screws serve
each wheel, one at each shaft end. The printed guard/opening is 6¾ × 4¾ inches
(171.45 × 120.65 mm). That opening is described for the adjusting screw; it
must not automatically be used as the entire shaft's available travel.
HB139 gives shaft nuts as 4⅞ inches in diameter and 4.18 inches across flats
(123.825 and 106.172 mm), with a hard copper plug associated with the locking
screw described at the start of HB140. M1475 is the locking screw, not the
main tension-adjusting screw.

Inspected HB asset `plate87.png`, the adjusting-wheel longitudinal/transverse
sections. It shows separate paired smooth rims, paired perforated disks, the
central boss, six radial formed diaphragm pieces, an oil-drilled shaft and a
rectangular adjusting bracket at each end. The six large disk holes and the
relieved diaphragm/spoke pieces need separate native features. It is not a
single solid annulus. HB `plate86.png` shows the analogous driving assembly
with toothed rims; HB `plate83.png` shows its installed, deeply relieved form.

SNL274:023–028 / 275:001–004 define each adjusting wheel as:

- Two rim entries printed/transcribed as M147 in the assembly row; HB235:049
  and SNL189:007 independently give M1471. Preserve the truncated SNL reading
  and check the survey identity mapping before selecting a canonical rim.
- One M1403 boss, two M1404 disks, five M1405X diaphragms and one M1405Y diaphragm.
- 36 button-head rivets ⅝ × 1⅞ inches, 24 of ⅝ × 2⅝ inches and 48 of ¾ × 2⅛ inches.

The driving-wheel assembly in SNL275:005–014 repeats those shared internals,
using two M1401 rims. Parent quantities are two idlers and two drive wheels.
Parenthesized constituent totals are shared whole-vehicle totals: four bosses,
eight disks, twenty X diaphragms and four Y diaphragms, not per-wheel quantities.
Each wheel therefore has 11 principal leaves plus 108 rivets before its shaft,
bushing, bearing/adjuster and oil hardware. Resolve the X/Y diaphragm distinction;
do not merge them just because the drawings look similar.

## Initial rail-fit calculation, not installed geometry

The current source-derived front shaft datum is SNL2 pixel (194,339),
X 9167.058208 / Z 1517.637951 mm. In the current closed 78-link route, a circle
of printed idler radius plus the 28 mm rail-eye envelope has a minimum signed
clearance of **−27.312005 mm** at that center (track segment 22). This predicts
interference; it is not a native BRep contact test.

Holding source Z and printed diameter fixed, the first rearward X shift that
reaches the same provisional 0.5 mm allowance used for the rollers is
**−29.380144 mm**, giving X **9137.678064 mm**, limiting segment 21. This was
computed against all current pin-to-pin capsule segments using scalar root
finding, without refitting the source calibration or changing pitch. It suggests
that an explicit static adjuster displacement may resolve the front wheel
interface without altering the whole track. The screw axis inclination, allowed
travel, bracket/hull openings and actual wheel-to-rail BRep gaps must still be
checked before adopting it. The source pick must remain independently recorded.

## Next geometry work

Reconcile rim identity and shared wheel counts, then build one complete idler
wheel from separate rim, disk, boss, X/Y diaphragm and rivet definitions. Retain
printed diameter and declared unprinted stock/contours. Add the shaft/bushing and
two adjusting mechanisms with owned hull openings; prove the static adjustment
fits both the wheel and the native tracks before mirroring. Drive tooth-count
and pitch conflicts remain separate in [drive preparation](R02-drive-research.md).

## Original-page and survey-identity follow-up

Directly inspected `SNL_G13_Project/sources/p274.jpg` and `p275.jpg`. The original
274 assembly constituent itself reads **M147**, so the truncated mark is not
merely a modern transcription error. The five-X/one-Y quantities and three
rivet groups are legible on the original pages. Keep that literal mark while
recording any future M147 ↔ HB M1471 cross-source decision explicitly.

Current frozen survey identities are:

| Source / role | Survey identity |
|---|---|
| SNL274:025, M147 rim constituent | `P_5000d4b91e36cf94` |
| HB235:049, M1471 rim | `P_9e0010cc050c6350` |
| SNL274:026, M1403 boss | `P_c8b6a3dddfe4ac9a` |
| SNL274:027, M1405X diaphragm | `P_d7f70339e5e1b287` |
| SNL274:028, M1405Y diaphragm | `P_a37a38cdb60e63a3` |
| SNL275:001, M1404 disk | `P_726db00696fd5fa8` |
| SNL164:027, M1401 drive rim | `P_9333bba91f74f16b` |

Also inspected SNL Plate 28 (`assets/p300-geometry.png`), the adjusting-wheel
section and elevation repeated in HB plate87. SNL274 associates callout 13 with
M1405X and 12 with M1405Y; the drawing exposes one upper diaphragm. The exact
X/Y difference remains unclear. The 48 larger rim rivets suggest 24 per rim,
consistent with SNL189:007. The 36+24 smaller rivets could distribute as six plus
four per diaphragm, but that is only a placement hypothesis until the joint
sections and rivet grip lengths are checked. A repeated geometric pattern must
not replace independent quantity and joint validation.

## Adjuster/shaft inventory follow-up

SNL214:021–028 gives two idler shaft assemblies. **Each** contains two M1477
nuts, two M1475 locking screws, one M1474 shaft, **two** M1409 bronze bushings
and two Q52C ⅜-inch pipe plugs. Do not infer a single bushing per wheel from the
handbook's generic singular wording. SNL214:026 explicitly gives M1409 OD
5.118 inches (129.9972 mm), ID 4 7/16 inches (112.7125 mm) and overall length
8 inches (203.2 mm). Those are independent bushing controls; the shaft clearance
and exact oil passage remain to be reconstructed.

The main tension screws are M1473 (SNL205:004), quantity four. They fit four
M1472 cast brackets (SNL41:008). SNL201:007 lists sixteen ¾ × 1¾-inch hex-head
cap screws, four per bracket. M1484 adjusting-bracket plates (SNL154:027),
M1483 shaft washers (SNL274:001) and M1479 guards (SNL103:016 / 149:016) each
have quantity four. M1479 appears twice by role; avoid counting both records as
separate sets of guards.

M1477 nuts have a shared SNL129:009 total of eight for idler/drive shafts.
M1409 bushings have a SNL43:011 total of twelve: two at each of two idlers,
two drives and two roller-pinion shafts. M1476 (SNL157:001), quantity four, is
the adjusting-screw locking plug; its copper material/locking role should be
checked against HB139–140 before geometry promotion.

Images inspected in this preparation (source hashes; inclusion in a future
geometry lock must be checked, not assumed):

| Source | SHA-256 |
|---|---|
| `references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate87.png` | `a16e3212f09537e419b6c8ae874bab7da7071596be7bcef638a6f613e52e7d3f` |
| `references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p300-geometry.png` | `4fbe1a62f80d30e6edc35bfe044a2612cbdaa733d982678654da164ba51381cd` |
| `references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p274.jpg` | `75981ec62f486c72ce1c1735dd82fe162fbfaf1198f8bebd432ea097d0ff57c5` |
| `references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p275.jpg` | `6d5ba6f467b880ef2a6d723664863438079b116154d8ef15c25975b86a2de6de` |

Do not automatically reuse the lower roller's ±190 mm axial centers or 123.825 mm
width for the idler rims. The idler drawing has relatively narrow separate rim
sections, whereas the lower rollers span paired link bars. The current track's
paired bar offsets are ±52 mm about each channel center, so a narrow rim centered
on the channel could sit between the bars instead of meeting a rail. Establish
whether the idler rims run on particular rail faces or another link surface,
then check the transverse placement against shell clearance, disks, bushings and
actual native track shapes. The planar −29.380 mm calculation above tests only
the XZ envelope and cannot settle this axial contact question.

## Native axial-contact probe (research envelope only)

A separate unsaved analytic rim envelope was checked against native link bars,
bushings and shoes at front track units 18–26. This used the candidate shifted
XZ center above, printed OD and an arbitrary 450 mm inner radius; it is **not**
an authored idler part. Only the positive-Y rim on the port bank was probed.

| Rim center from track center | Trial width | Minimum native rail gap | Interpretation |
|---:|---:|---:|---|
| +190 mm | 50.8 mm | 16.608 mm | A narrow rim at the roller channel center misses both bar faces. |
| +190 mm | 90 mm | 0.5 mm | Wide enough to overlap both rail bars. |
| +190 mm | 123.825 mm | 0.5 mm | Roller-like width bridges both bars; not an idler dimension claim. |
| +242 mm | 50.8 mm | 0.5 mm | Narrow rim meets the outside bar only. |

The +242 / 50.8 mm trial left about 25.884 mm to the nearest bushing and
78.441 mm to the shoe, with no candidate material overlap. The wider +242 mm
trials also met that bar, but their outer axial extents need shell checks; they
are not recommended placements. No whole-wheel, opposite-hand, hull, shaft or
adjuster qualification follows from this probe. Axial position and rim width
must be supported or explicitly inferred during the next physical reconstruction.

The narrow +190 / 50.8 mm rim has another viable **geometric** interface: the
native track bushings. A follow-up probe solved distance to the actual pin
centers using the 20 mm bushing radius rather than the continuous rail capsule,
then checked the native shapes. It achieved 0.5 mm to a bushing with about
16.6 mm axial clearance from either link bar, about 53.218 mm from the shoe,
and zero tested overlaps. This alternative is closer to the source shaft X;
its exact probe coordinates are recorded below. It does not establish which
interface the historical idler used. Compare the relatively narrow source rim
sections and the handbook's wording before adopting either candidate. The
29.380 mm rail-fit shift is therefore an investigated alternative, not the
recommended final installation.

Bushing-contact candidate: X **9163.195854 mm**, Z **1517.637951 mm**, a rearward
shift of **3.862354 mm** from the current source datum. Nearest native bushing is
`PortTrack_Unit021_Links_ChannelB_Bushing`. The trial uses the same arbitrary
450 mm rim inner radius; only its outer/axial envelope is under investigation.

## Follow-up for the shaft/adjuster installation

The rotating wheel/bush subset is now implemented in
[R02-idler-wheels.md](R02-idler-wheels.md); the earlier “research only” statements
above describe the preparation stage and its unsaved contact probes.

The relevant handbook legend is **HB:legend:140:001–013**, not page 139's
analogous drive-wheel legend. Its callouts identify 3 and 7 as M1472 bracket,
4 as M1477 nut, 5 as M1475 locking screw, 8 as M1474 shaft, 9 as M1484 plate,
10 as M1479 hull guard and 11 as M1473 main tension screw. Both HB87 and SNL28
were re-inspected during wheel implementation. Do not confuse the large hull
reinforcing plate, cast bracket and small guard as a single cover part.

SNL170:003 adds **½ × 1⅝-inch button-head rivets** for M1484 against M1962B
and M1962A, five per listed plate pairing. Its whole-vehicle total 28 also
includes transmission-frame and SH956B uses, so it is not an idler-only total.
Resolve the number of paired hull/adjuster plates and allocate the shared rivet
identity before creating occurrences. SNL201:007 independently gives sixteen
¾ × 1¾-inch cap screws, four per M1472 bracket. The eight heads visible around
the figure's rectangular opening cannot simply be interpreted as eight of those
cap screws per bracket.

SNL2 depicts the adjusting mechanism inclined in the side view. The current
wheel-only fit holds source Z fixed and shifts X by just 3.862 mm. When the
shaft/bracket assembly is reconstructed, derive its axis from independent source
picks and solve adjustment along that direction; do not silently equate the
current numerical X search with the mechanism's historical motion or travel.
The current source pick and all offsets must remain separately available.

SNL149:013/014 each list **one** M1962B/A outside front-upper plate, matching
`hull_port_front_upper` and `hull_starboard_front_upper`. Therefore the two
explicit five-rivet pairings in SNL170:003 establish **ten** outer installation
rivets, not automatically twenty for all four M1484 plates. The other two
M1484 attachments and the remaining uses of the shared 28-rivet total still need
reconciliation. Shared rivet survey identity: `P_6c6091ce378e73b1`.
The current H01 front adjuster hole is a provisional **95 mm round bore** at
source pixel (194,339); it must be replaced or extended by the shaft/guard-owned
sliding-interface construction, rather than assumed adequate for the printed
bushing diameter or source opening.

### Frozen identities for the next installation subset

| Role | Source row | Survey identity |
|---|---|---|
| Shaft | SNL:214:025 | `P_b6e2672cc73e5dd6` |
| Shaft nut | SNL:214:023 | `P_7dadf20f3a38ad7e` |
| Locking screw | SNL:214:024 | `P_6d347cf62b3f0d8d` |
| Oil plug | SNL:214:027 | `P_4a25f9905c502b80` |
| Tension bracket | SNL:41:008 | `P_3c3719fa79b01d91` |
| Bracket plate | SNL:154:027 | `P_31f60aba7a828d11` |
| Main tension screw | SNL:205:004 | `P_8a12195f34e8cdd8` |
| Shaft washer | SNL:274:001 | `P_32da1165d6aa911c` |
| Copper locking plug | SNL:157:001 | `P_7994ad5761f72e29` |
| Hull guard | SNL:103:016 | `P_16942102ca920716` |
| Bracket cap screw | SNL:201:007 | `P_59c5314261c76405` |
| Shared plate rivet | SNL:170:003 | `P_6c6091ce378e73b1` |

Q52C oil plugs share the identity already used for lower rollers. M1479
guard records SNL103:016 and SNL149:016 refer to the same identity/set.
These locators establish identities, not yet geometry or a completed installed BOM.

### Section refinement to resolve before closing the wheel packet

The delivered provisional disks attach at the outboard rim faces. A closer
reading of the narrow rim/disk lines in HB87 may instead support an inboard
attachment land; that reading is not yet resolved. Test both axial arrangements
against the original section, the shared boss/bushing stack and full native hull
clearance before treating either as historical geometry. Axial placement also
affects whether narrow rims can meet link bars instead of bushings. Do not move
rims to ±242 mm merely to obtain rail contact without rebuilding/checking disks,
rivet heads, diaphragms, boss interfaces and the foremost roller. The present
bushing-contact arrangement remains explicitly provisional. The source's flatter
central diaphragm trough is another queued shape refinement.

### Integration notes for shared native definitions

Reusing the existing `roller_plug` Q52C definition in an idler shaft will require
scoping the roller validator by roller installation IDs, rather than selecting
all `roller_*` definitions anywhere in the tank. Likewise, when drive wheels
reuse `wheel_boss`, disks, diaphragms, bushes and rivets, scope the idler validator
by `PortIdler_` / `StarboardIdler_` installation IDs and reconcile drive quantities
separately. Do not duplicate physical identities simply to bypass family checks.
The current validators correctly cover their present installations; these are
required extensions before shared definitions gain additional installation roles.

## Follow-up implemented

[The mounting packet](R02-idler-mounts.md) now records the qualified partial
shaft/adjuster increment. It implements the shared-definition scoping rules,
source-complete nine-part shafts, ten explicitly allocated outer-plate rivets,
fixed source-axis bracket frames and support-owned hull openings. The tested
inboard land/nested-disk reading and flatter diaphragm trough supersede the
earlier provisional section; they remain inferred geometry. Historical fit,
threads, inner retention and exact casting/guard forms are still open.
