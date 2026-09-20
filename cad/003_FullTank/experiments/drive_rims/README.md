# Isolated drive-rim study

This is preparation for the [drive-wheel packet](../../packets/R02-drive-wheels.md),
not an integrated tank component release. The 35- and 37-tooth hypotheses
preserve the conflict between original HB130/133 and HB119. Neither count is
selected as historically definitive by this experiment.

The native studies each contain two port-side rim solids at the unchanged
calibrated drive axis. The overall 39.237-inch diameter, 32.75-inch inner diameter
and 2-inch width come from the handbook. Assigning the printed inner diameter
to the annular bore is provisional. Groove radius 25.7 mm, root radius 462.5 mm,
lip inner radius 450 mm, 430 mm rivet circle and the axial land are inferred.
Circular reliefs provide an exploratory profile, not a conjugate tooth form.
Fillets, exact casting sections, manufacturing allowances and engagement remain
unqualified.

Each count was sampled at eight phases within one tooth interval. Both port
rims clear the existing physical assembly in all samples: 30 candidate material
pairs per phase, zero overlap above 0.00001 mm³. This establishes static material
clearance only. It does not establish engagement, and the study omits the new
drive disks, boss, diaphragms, shaft and neighboring roller pinion.

Moving the current shared idler disks into these trial rims produces about
936,049 mm³ overlap per side for 35 teeth and 910,466 mm³ for 37 teeth. Their
470 mm rivet circle also differs from the trial's 430 mm circle. Thus these
particular rim hypotheses and the existing disk reconstruction cannot be
integrated together unchanged. Reconcile the shared disk/rim interface from the
source sections and qualify both drive and idler installations before adopting
either construction. The experiment does not prove that the source disks differ.

The [comparison page](comparison.html) shows the inspected source and both native
studies. `build/report.json` retains every phase, overlap, source conflict and
the precise native/script hashes. `reference_native` preserves the 20 native
dependencies of the earlier lower-support nominal trial; its manifest binds
those files to the recorded authored inputs. It is an experimental baseline,
not the current qualified delivery.

Run from the repository root:

```sh
python3 cad/003_FullTank/experiments/drive_rims/probe.py
```

The script verifies the preserved baseline, uses the installed FreeCAD runtime,
and asserts that it has not changed any tank-authored inputs. Standard progress
snapshots are reserved for integrated, inspected assembly milestones.

## Common interface and installed study

`common_fit.py` retains the first smaller-disk/deeper-land trial in
`common_fit_build`: it has 24 material intersections per 121-part wheel fixture.
The ring lands hit diaphragm ends and the outer short rivets, despite positive
rim/disk bearing faces. That variant is rejected.

`common_fit.py --refined` additionally shortens the inferred diaphragm flange
to 410 mm radius, its web end to 404 mm and the three short-rivet radial pitches
to 25 mm. Both fixtures reuse the same native disk, boss, diaphragm, bushing and
rivet definitions. Each now has zero material overlaps in 358 candidates and
two rim/disk bearing faces of about 82,668 mm². These are geometric feasibility
results, with the source-count conflict, exact formed/cast profiles and locally
overhanging rivet heads still open. The dimensions are not accepted model inputs.

`installed_fit.py` places both refined idlers and two 35-tooth drive wheels at
the four recorded installation axes, replacing the earlier idler components in
its audit context. All 1,626 candidate pairs are clear in the 5,074-component
physical context. Its native file contains only the four candidate wheels;
the full-context image combines those wheels with the preserved reference
assembly. Drive shafts, bearings, retention and roller-pinion engagement remain
absent. No main tank geometry has been changed by these experiments.

The accepted lower-support input fingerprint is recorded in
`authored_input_fingerprint.json`; regeneration stops after those authored
inputs change, until a deliberate review/rebase. Exact executed script copies
are retained alongside the three successful study reports for provenance; the
current launchers add this archive guard. The rejected first fixture report
records its earlier execution hash.

`round_teeth.py` applies an inferred 3 mm radius to the 70 axial crest edges of
the 35-tooth working branch. Native subtraction confirms zero added material,
14,258.225 mm³ removed per rim, and unchanged rim/disk bearing area. The outside
cylindrical radius remains 498.3099 mm. This candidate therefore inherits the
earlier material-clearance result at unchanged placements. It remains an
approximate tooth form, with continuous engagement and the count conflict open.
The refined idler, refined drive, installed context and rounded-drive images
have been inspected alongside the source arrangement; they are preparation for
typed integration and do not advance the tank's standard milestone number.

The refined common geometry and rounded 35-tooth branch were adopted as explicit
partial authored geometry on 20 September after snapshot 008. Integration
qualification is pending in the [drive packet](../../packets/R02-drive-wheels.md).
The archived experimental scripts intentionally retain their original input
guard; later main-model changes do not retroactively qualify these studies.

## Qualified integration

The corrected common-interface and rounded 35-tooth working hypothesis is now
in the qualified partial tank stage, preserved as snapshot 009. All thirteen
parameter trials pass, including the 37-tooth sensitivity case. Historical
tooth count and engagement remain unresolved. The studies above retain their
original inputs and earlier acceptance state; they are not current build launchers.
