# Complete operating handles and pivot joints

`operating02` builds M738B port and M738A starboard handles, M747/M746 fulcrums,
and two complete M776/M768/cotter joints. Ten additions use seven definitions.
Four existing upper selector arms/jaws change; all journal, oilway and lower
linkage material outside the explicit upper-arm edit envelope is preserved.
Every inherited occurrence frame remains fixed.

The source packet is [operating_source_review02.json](operating_source_review02.json).
The printed 37-inch handle length is provisionally interpreted as the canonical
radial extent from the lower eye extremity to grip end, 939.8 mm. It is not
asserted to be a printed pivot-to-tip or developed-centerline datum.

## Initial interference and revision

`operating01` is retained with its eight failed interference pairs. Both handles
met the straight selector stems and front hull plate; each cotter eye lead also
met its bolt by 0.06157 mm³. The original builders and source controls remain
available, including copies in `operating_diagnostics01/first_interface`.

The second trial uses a 50 mm radial pivot drop and 78 mm tangential fulcrum-ear
offset. The handle heel wraps around the shaft, rises into the selector plane,
and has a 20 mm upper return. The low-selector upper arms move 45 mm outward,
consistent with the splayed form in the source plan. Their actual C mouths now
receive the handles, with 0.45 mm fore/aft face clearance. These unprinted forms,
stocks, positions, bend details and the selected eight-degree lateral angle are
reconstruction estimates, not a source tracing or motion qualification.

The specific M776 assembly in the original SNL23 specifies a 3/16 x 1-inch split
pin. The generic SNL141 1-1/2-inch row also names M776. The shorter, specifically
listed pin is selected here; the conflict remains open. Its split plane lies
through the crown nut's axial slots. Moving the inferred near-eye stand-off from
0.2 to 0.75 mm removes the small lead collision without changing the source leg
length or original bore clearance. Measured cylinder/toroid/tail centerlines are
23.175 + 0.872665 + 1.352335 = **25.4 mm** per leg. Eye/junction convention and
formed-wire details remain estimates. Full material and strict STEP checks pass.

## Mechanical evidence and limits

Nominal 12.7 mm and variant 13 mm handle stock each pass **419 local checks,
53 context pairs without exemptions and 25 strict native/STEP comparisons**.
A fresh prototype rebuild reproduces 126 BReps and 9,116 persistent properties.
The actual head and nut bearing area is 759.591208 mm² at each joint. Both low
selector drive faces engage 410.393925 mm² on port and 388.457659 mm² on starboard
when the nominal clearance is taken up. The high selectors clear by 3.933679 mm.
The complete handles clear the front hull by 14.082184 mm.

Displaced checks demonstrate loss of seating, over-travel interference, cotter
withdrawal resistance and blocked crown-nut rotation. This establishes only the
selected local static geometry. Trigger/pawl parts, separate gates/stops, braking
interconnection, springs, spacing, reverse controls and complete seat support
remain unbuilt or unfinished. No full operating cycle or hand-space claim is made.

## Source discrepancy must stay visible

Six saved views were inspected, including unchanged SNL6 plan and HB113 side
registrations. Grip residuals are **47.16/48.59 px in plan and 49.41 px in side**,
well beyond the 5 px pick allowance. The pivot residual is 4.92 px. The retained
high-rod eye discrepancy is still 13.53 px. These are not passing historical-fit
results, and neither source registration is refitted.

[Source diagnosis](operating02/source_comparison_diagnosis.json) shows why a
simple pose adjustment is insufficient. The inferred cap-to-current-pivot reach
is 1013.62/1015.82 mm, versus the actual 922.49 mm. The source views disagree in
fore/aft coordinate by 35.18/38.73 mm. Literal transfer of the side cap to the
current driver station puts it 44.59 mm beyond the current hull front plane.
The source side cap radius from the main shaft is 940.88 mm, close to the printed
939.8 mm. That raises a plausible alternative length datum; it does not prove it.

The ambiguous printed datum, source feature identities and local scale, depicted
configuration, and absolute driver/hull placement require reconciliation. Keep
this as an explicit evidence decision. Do not stretch the stock, move whole
subassemblies or refit cameras merely to make the overlay agree. Current geometry
is a mechanically checked reconstruction approximation, not a historically
qualified installation. This evidence review should precede fixing the trigger
and grip fittings to the current upper blade.
