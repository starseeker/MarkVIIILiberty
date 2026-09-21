# I03 — MX5 case mounting trial

Status: **native installation trial; casting-profile review remains open**.
This packet does not replace the accepted vertical-controls candidate or modify
the standard tank. It investigates the four M263 case attachments, with separate
studs, castle nuts, split pins and bevel washers.

## Identity and evidence

| Physical item | Survey identity | Installed trial quantity | Source |
|---|---|---:|---|
| MX5 stud | P_c5b4d785b6867abb | 4 | SNL241:028 |
| 3/4in SAE castle nut | P_c3bb5fc9299bfab2 | 4 | SNL241:029 |
| 1/8 × 1-3/8in split pin | P_715e37e46e3ce9b8 | 4 | SNL242:003 |
| MX13 bevel washer | P_6e5a15454080a055 | 4, conditional allocation | SNL267:006 and HB Plate121 |

SNL59:031/033 and 60:003 own the case and four stud assemblies. The assembly
listing gives **5-1/2in**, while SNL241:026/028 gives **5-5/8in** for the detailed
assembly and physical MX5. The trial uses 142.875mm; 139.7mm remains an explicit
alternative. Both specify 19.05mm diameter, 38.1mm US-thread span and 28.575mm
SAE-thread span. Assembly identities P_50d2ee4ba9ef6f71 and P_21218b61a7580c24
remain distinct. The pin listing continues onto page 242 and explicitly assigns
four sets to M263.

The source lists 24 MX13 washers overall (SNL267:006), but 20 in the transmission
frame with brackets/caps (SNL96:007). That assembly separately lists 20 MX1
bracket-to-channel bolt assemblies (SNL96:012; physical bolts SNL28:003).
HB printed 204 Plate121 labels MX13 at the case/channel joint. Interpreting the
remaining four washers as case attachments reconciles these quantities, but is
not an explicit four-washer entry in the SNL59/60 case list. Frame MX1 bolts and
their 20 washers remain future work.

Eleven source records and linked identities are checked against the read-only
survey. Original catalogue pages, the marked handbook section, HB printed 126
Plate79 photograph and SNL Plate23 were inspected. The asset number `plate121`
is a plate number, not printed page 121.

## Geometry and interfaces

The trial retains the accepted transmission datum: X forward, Y port, Z up,
origin [1825.2303627827532,0,849.2335104357661]mm in the tank frame. It adds 16
physical occurrences under `TransmissionCore/TransmissionCaseMounting`, using
four joint containers. Each owns one stud, nut, pin and conditionally allocated
washer; assembly identities do not add physical solids.

The stud axes run along X, at Y ±118mm, centered in the inherited case webs.
Upper/lower Z stations are 343.636318786 and −287.334459202mm. Source-length studs
derive their embedded ends from the washer/nut stack. Four integral, bored
44mm-diameter casting bosses extend from the frame face atX−227.148571429 to
X−118.198571429mm. These long bosses are a hypothesis, not measured casting
geometry. The blind bores retain 0.3mm end clearance and 4mm end stock. Thread
flanks are omitted; smooth-envelope checks do not qualify thread retention,
torque, casting strength or clamping load.

The frame's existing exterior planes and placements remain fixed. Inside flange
stock tapers from an estimated 12mm at the web to 8mm at the free edge. A34×30mm
bevel washer follows this slope and presents a flat nut seat. Lower washers
are turned 180degrees about the stud axis. The exact rolled section, root fillets,
washer dimensions and casting blends remain unverified. Case receivers and both
channel bores are actual material removals, not display-only holes.

The saved trial has 1,407 valid physical leaves:16 new, three changed and 1,388
unchanged from the accepted candidate. The shared existing 3/4in castle nut is
reused. Four split pins share an analytic formed-pin definition. Both straight
legs of the older shared pin were also checked and are present; no older pin
was repaired or replaced by this trial.

## Visual comparison and unresolved shape

The source overlay retains the input-bearing calibration,0.9211419753mm/pixel
and shaft origin[579,493]px. It sections the case/frame atY118mm to expose the
mounting web. This is not asserted to be the manual's exact cutting plane.
No source warping or recalibration was used to improve the fit.

The upper boss projects roughly 55–66mm forward of the visible upper wing
boundary at the stud-axis row; the lower discrepancy is roughly 10–28mm.
These are broad manual visual brackets, not metrology. The inherited frame
face is itself about 25–36mm forward of the illustrated upper face and 1–11mm
forward at the lower face. A straight frame, a slightly leaning source drawing
and unresolved out-of-plane casting detail contribute to the uncertainty.
HB's photograph does not establish the required boss depth.

The source lengths and washer callout support the attachment interpretation,
but a clear mechanical fit does not settle this visible discrepancy. Preserve
the trial for comparison. The next geometry decision must consider the M263
foot profile, stud assignment and inherited frame offsets together, then either
revise the mounting architecture or explicitly accept its bounded approximation.

## Validation and reproduction

Nominal material/interface checks, independent geometric witnesses, parameter
trials and STEP results are retained with the
[native trial](../experiments/drive_chains/transmission_case_mount_trial_build/MX5CaseMountTrial.FCStd).
All 183 affected material pairs,61 interface distances,84 independent geometric
checks,19 native/STEP comparisons and three local parameter trials pass.
Final numerical results are recorded in `review_status.json`; no historical-fit
qualification is implied by a numerical pass. Twenty standard CAD files and 58
earlier progression images remain byte unchanged. Two new trial images record
the mounting arrangement and joint section.

The first washer had a full-period elliptical bore edge. STEP Boolean differences
were empty, yet explicit mass integration differed by 0.001868mm³. Preserving two
analytic half-cylinder faces and half-ellipse trims removes that discrepancy.
No BRep tolerance was manually enlarged. Diagnostic alternatives and the rejected
exchange are preserved. An independent check initially expected over 4mm of
nut/channel separation; the channel web is actually the nearest surface, at
2.7125mm. The corrected check measures that physical gap.

```sh
python 3 cad/003_FullTank/experiments/drive_chains/transmission_case_mount_trial.py
python 3 cad/003_FullTank/experiments/drive_chains/check_transmission_case_mount_trial.py
python 3 cad/003_FullTank/experiments/drive_chains/check_case_mount_variants.py
```

The trial builder reopens and checks the accepted parent before mutation, saves
and reopens the derived model, and verifies all unaffected placements/shapes.
It checks affected pairs against the retained transmission and the standard tank
context, with the same explicitly superseded receivers as the parent candidate.
Sensitivity cases rebuild the 19 local shapes with the shorter printed stud and
10/14mm flange-root stock; their scope excludes external context and STEP.

Standard tank 011, its transparent companion and the full-tank coverage remain
unchanged. Pump/support, MX1 frame attachments, brakes, oil circuits, long
controls, integration and other tank interiors remain unfinished.
