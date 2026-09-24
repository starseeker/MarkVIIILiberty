# Shared low-speed and foot-brake spring supports

[RearLowSpringBrackets.FCStd](RearLowSpringBrackets.FCStd) contains two M4136
supports, four source-listed rivets and the revised receiving channel: seven
occurrences using three shared definitions. It preserves the M4135 mounting
holes from the [preceding guide study](../high_spring04/README.md), then adds four
vertical holes. This prototype is **not integrated** into the full development
assembly, which remains at 3,226 occurrences / 558 definitions / 347 groups.

The original SNL170 scan confirms two half-inch by 1⅞-inch rivets per M4136;
the global quantity 42 includes other applications. SNL38/63 and the handbook
identify two brackets. HB104 and the SNL6 plan support a U-like member spanning
adjacent short brake connections. The exact section, mounting stack and spring
attachments remain uncertain. The [source review](../low_spring_source_review04.json)
retains the observations and earlier hypotheses. M4129's relationship to this
mount remains open; no additional shared fasteners have been invented.

## Selected approximation and retained failures

Each U has 6.35 mm stock, 38.1 mm width along X, 317.5 mm outer transverse span
and 114.3 mm height. Its base is at X = 2368, Y = ±650.875, Z = 583.85 mm.
Estimated transverse spring holes have diameter 6.65 mm and centers 101.6 mm
above the base. Internal bend radius is 6.35 mm. These dimensions and stations
are reconstruction parameters, not printed dimensions. Regenerate the native
from `low_spring_controls04.json` using `trial_rear_low_spring_brackets.py`;
editing metadata alone does not change the solid.

The rivets pass through 12.7 mm combined grip. Interpreting the catalogue length
as unformed shank leaves a large upset: 31.75 mm diameter and 9.894682 mm height.
Its stock volume and complete bearing annulus are checked. The stock-length
datum, head form and any alternative M4129 grip stack remain hypotheses.
The stock variant uses 6.85 mm plate, 13.2 mm grip and a recalculated upset,
while retaining the outer dimensions and attachment height.

| Candidate | Finding |
|---|---|
| low_spring01 | Initial base crosses track-fulcrum feet, levers and rivets: 12 failed material pairs. |
| low_spring02 | Wider U and rearward station leave a 48.259244 mm³ starboard low-lever overlap. |
| low_spring03 | A 6 mm forward shift clears bracket checks, but both provisional low-speed spring corridors cross their levers. |
| low_spring04 | Raising the ends 38.1 mm clears the tested corridors and moves the attachment toward the depicted spring level. |

The earlier geometry and failed checks remain intact. Variation03 was generated
and extracted only; variation04 is the independently checked stock variant.

## Saved-artifact checks

Nominal and thicker stock each pass 36 native/interface checks, 21 local material
pairs, eight surrounding-material pairs and ten strict STEP comparisons (three
definitions and seven installed shapes). Context screening includes all 3,226
parent occurrences, 5,316 retained standard solids and the six M4135 prototype
members. Checks cover local links after relocation, actual spring passages,
the open U, receiving holes, base support, rivet bearing and source stock volume.
STEP checks retain the existing material, tolerance and converged-mass criteria.

Fresh nominal generation passes seven reproduction checks: nine archive BReps,
662 persistent properties, all occurrence frames and hierarchy agree, with no
allowed property differences. Whole FCStd archive byte identity is not claimed.

The [corridor study](../low_spring_routes04/route_checks.json) and stock variant
each pass 27 material comparisons. Four 19.05 mm rod-core witnesses use Bezier
paths with horizontal end tangents, perpendicular to the two differently
oriented pin axes. They stop 38.1 mm short of each measured pin center. Four
19.05 mm spring-core envelopes stop 25.4 mm short of each proposed attachment.
Brake-pin washer targets are provisional offsets, not modeled M567 washers.
These are space checks, **not completed SH946D/SH946E rods or M564 springs**.
Forks, socket engagement, washers, hooks, spring stock and service remain open.

The side overlay reuses the existing SNL6 registration unchanged. Raising the
ends brings the upper attachment nearer the drawn M564 spring band, but the
provisional springs slope down toward the current brake-pin heights while the
drawing appears more nearly level. That disagreement remains unresolved. The
view cannot establish transverse span or hook topology, and HB104 remains an
uncalibrated photograph. Estimated new anchors are not independent camera holdouts.

## Continuation

Resolve M4129 attachments and the actual short-connection forks, M567 washer
applications and spring ends. Preserve SH946D/M569C for the short track links
and SH946E/M569A for the short low-speed links; M578/M573 are the longer rear
rods. M564 has four rear-control applications and a separate fan-jockey
application. Complete the connected family and transfer its tested geometry
into the hierarchy, retaining the stated approximations and source discrepancies.

Read-only recovery reuses the saved evidence:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_rear_low_spring_study.py
```

The [study receipt](../low_spring_study_receipt01.json) binds the evidence,
prototypes, failed alternatives and progression images. The complete standard
tank goal remains active; pose variants remain deferred.
