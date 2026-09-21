# I03 — small planetary gears and riveted input disks

This packet populates the small epicyclic train in the isolated transmission
candidate. The standard tank remains milestone 011 pending transmission,
mounting and interface completion. Small planet support stacks remain a separate
unfinished component family; their absence is visible in the inspection views.

## Inventory and source interpretation

| Part | Mark | Installed quantity | Survey identity |
|---|---|---:|---|
| Small sun and sleeve | M267 | 2 | P_2a56afba1c59acc7 |
| Sun sleeve bush | M268 | 2 | P_f116151490294cc9 |
| Small planet gear | M270 | 6 | P_656200c1c85d813a |
| Small internal ring gear | M275 | 2 | P_8d6f40ea97f90be5 |
| Small ring input disk | M276 | 2 | P_aa00dc7ea9b9fb0c |
| Button-head rivet, ½ × 1⅞ inch | — | 32 | P_b82829647b7a14b6 |

SNL144 specifies the sun/bush assembly and six small planets. SNL165 specifies
one disk, one ring and sixteen rivets per small-ring assembly; there are two
assemblies. Assembly catalogue records do not create additional physical solids.
The source rows and inspected original-image hashes are retained in
`transmission_small_sources.json`.

HB126 prints 30 teeth for M267 and 78 for M275, both 5–7 diametral pitch. The
common pitch and simple epicyclic arrangement imply **24 planet teeth**:
`(78 − 30) / 2`. This is a derived count, not a located printed M270 dimension.
Pitch radii are 76.2, 60.96 and 198.12 mm; planet centers are at radius 137.16 mm.
Three planets satisfy the assembly phase condition `(78 + 30) / 3 = 36`.

HB120/122 describes the cross shaft driving disk D and small ring V. When the
small sun F is restrained by the high-speed brake, the small carrier drives the
large annulus. The large sun also follows the cross shaft. These counts imply
small-carrier speed `78 / 108` of input and output speed
`(18 + 72 × 78 / 108) / 90 = 7 / 9` of input. The resulting reduction of
1.285714 agrees with the handbook's 1.285 figure.

**Printed conflict:** HB126 also assigns 30 stub teeth to M276 disk D. That
disagrees with HB120's description of a disk splined to the cross shaft and
SNL165's separate riveted disk/ring components. This reconstruction uses a plain
disk with the shaft's ten splines. It does not reinterpret that row as the planet
tooth count or silently correct the frozen survey.

## Geometry and approximations

The existing involute generator supplies cubic B-spline flanks and analytic
tip/root arcs. The 20-degree pressure angle, 0.2 mm tooth thinning, radial root
continuations and omitted cutter fillets remain inherited assumptions. The
two-pitch interpretation supplies addendum 25.4/7 mm and dedendum 1.25 times that.
The even 24-tooth planet requires a half-tooth phase relative to the earlier
27-tooth train; the internal ring's void profile also receives a half-pitch phase.

Plate22 picks x1064–1104 control the small gear faces. The disk outer face uses
x1017 and the sleeve inner end x1294. All use the unchanged conditional
0.725714 mm/pixel scale. Manual picks do not establish manufacturing dimensions.
The selected source planet axis y739 gives a radius 7.257 mm smaller than the
printed tooth geometry; this discrepancy remains explicit.

The ring has a separate rear attachment rim meeting the disk's 12 mm web.
Sixteen axial holes receive separate rivets on an inferred 215 mm radius.
The printed 47.625 mm rivet length is the unformed shank length, not the installed
grip: 8 mm is assigned to forming the tail head, leaving 39.625 mm grip. The
spherical-cap tail has the volume of that assigned stock. The original button
head uses the same inferred cap shape. Head contour, upsetting allowance, lap
profile, fit and attachment strength are not historically established.

The first material check found each forward rivet head intersecting the ring's
stepped rim by approximately 203.14 mm³. Explicit axial head-access counterbores
now run through that forward rim to the head-seat plane, with radius equal to
the head base plus 0.25 mm. This inferred access feature retains the printed
rivet dimensions and leaves the gear teeth unchanged. Its radial envelope leaves
approximately 2.32 mm of nominal stock outside the tooth roots; no strength or
fatigue adequacy is asserted for that inferred wall.

The native/source overlay also exposes an axial rivet-center discrepancy: the
illustrated upper rim rivet is approximately centered at x1065, whereas the
modeled flat disk web and rivet grip place its center about 15 mm farther
outboard. The source shows a swept transition toward the rim that the current
flat-web approximation does not reproduce. Reconcile that casting transition
and the surrounding case envelope as the small support stack is populated;
nominal clearances do not resolve this source discrepancy.

The small sun carries a long sleeve splined to the existing high-speed drum.
Its separate M268 bush rotates on a smooth shaft journal. The journal retains
the inherited 28.8 mm root radius and removes only the spline crests within the
two bearing intervals. Other shaft material and the central/end spline regions
are protected. Bush, spline and axial fits are reconstruction choices. M290
retaining rings and the complete brake-bearing installation remain pending.

## Reproduction and acceptance

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_small_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_small.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_small_review.py --stage cad/003_FullTank
```

The reopened candidate has 1,059 valid single-solid occurrences: 46 new, one
revised shaft and 1,012 unchanged. All 166 material candidate pairs are clear;
182 specified contacts/gaps, ten native tooth counts and six mesh checks pass.
All 47 new/changed solids preserve material through STEP with empty two-way
Boolean differences, bounded native tolerance and no import tolerance inflation.

Thirty independent local trials, eight native dimension checks and seven
intentionally displaced STEP checks pass. Eight images were actually inspected;
the saved `visual_review.json` binds them to the native and qualification reports.
The [combined cutaway](../../intermediate_snapshot_iso_transmission_small_001.png)
and [small-train oblique](../../intermediate_snapshot_detail_transmission_small_001.png)
are preserved separately from the standard tank milestones. The checker deliberately misclocks gears, disks and splines, moves
bushes and rivet heads into their receivers, and samples nearby compatible
gear phases. These local checks do not qualify full motion, loads, wear,
historical fits or a complete parameter envelope.

Next populate M271/M272 bushes, M274 pins and their retention, M273 pin rings,
M317 fastening, M290 sun retainers and M265/M266 brake bearings. Central bevel
and input assemblies, case fastening, brakes, controls, mounting, lubrication
and standard-tank integration also remain unfinished.
