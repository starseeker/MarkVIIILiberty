# Seat stays and support connections — 27 September 2026

The support review found **four omitted stays and their fastening stock**. The
earlier [seat-side prototype](../driver_seat_study/BUILD.md) remains a useful
construction study, but its estimated **16.3 mm bearing bores cannot receive
the printed 19.05 mm seat bolts**. No historical installation was accepted by
that prototype's geometry checks. This packet corrects the next construction
inputs; it does not alter the frozen prototype or claim completed supports.

## Directly reviewed source

| Source | Original entry | Construction consequence |
|---|---|---|
| SNL222:007–008 | Two front SH289B stays; two rear SH289D stays | Build four distinct installed stays, with shared front/rear definitions where appropriate. |
| SNL31:005 | ½ × 1⅜-inch bolts, plain nuts and lock washers; one per SH289B/SH289D stay | Four full 12.7 × 34.925 mm lower mounting bolts, four nuts and four locks. |
| SNL33:009 | Four ¾ × 2⅜-inch bolts, plain nuts and lock washers, securing the seat to stays | Four full 19.05 × 60.325 mm upper bolts, four nuts and four locks; rebuild the receiving bores. |

The upper-bolt row literally names **SH289A and SH289B**, whereas the stay list
and lower-bolt row name **SH289B and SH289D**. Original scans confirm both
readings; this is not a transcription correction. Use B/front and D/rear as a
provisional selection, retain the printed upper-bolt functional application,
and keep the conflicting A/B labels unresolved.

Inspected original rows are saved as [lower bolts](evidence01/p031_support_rows.png),
[upper bolts](evidence01/p033_support_rows.png), and
[front/rear stays](evidence01/p222_support_rows.png). The broader catalogue search
is a discovery list, not a declaration that every returned item belongs here.

## Geometry to build next

Use [interface_constraints.json](evidence01/interface_constraints.json) with the
saved `driver_seat_study/trial06` geometry. A proposed 19.3 mm receiver provides
0.125 mm radial clearance around the printed bolt; that clearance remains an
engineering estimate. All four bearings share the revised definition. Preserve
the bearing-rivet source stock and actual pan contact when rebuilding them.

The inherited section picks suggest front/rear projected stay lengths of
264.234 / 256.691 mm. These are conditional construction distances, not printed
lengths. Their lower-joint identities and transverse positions are unproven;
the unequal slopes do not qualify parallelogram motion or adjustment travel.
HB6 remains an uncalibrated perspective topology reference.

Complete the two M788 angles and eight 12.7 × 41.275 mm bolt/nut/lock stacks
from the preceding evidence packet. The intended additions total 54 occurrences:
four stays, their 24 fastener pieces, two angles and 24 angle fastener pieces.
M786/M787 extensions and the bearing definition require explicit revision.
The current folded-foot hypothesis does not establish which surfaces historically
belonged to the separate M788 angles. Resolve that part boundary and mounting
allocation while preserving the full shaft stock and real floor constraints.
Do not merely attach new angles to an already complete estimated folded foot.

Check saved solids, actual receiving holes and contact, every nearby physical
part, strict STEP exchange, a relevant variation and a fresh rebuild. Reuse the
fixed source section and inspect the complete connected assembly before any
integration. Support completion cannot by itself settle the unresolved absolute
shaft/seat position or source-profile differences.

The initial packet searched the seat assembly and bearing entries but omitted
alphabetical STAY entries and generic BOLT applications. Future receiving-part
packets should search both exact piece marks and functional descriptions across
the catalogue before selecting unprinted bores or declaring an inventory complete.
Retain the original failed assumption so its correction remains traceable.
