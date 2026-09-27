# Driver seat reconstruction packet — 27 September 2026

The next geometry is the complete adjustable seat and its connection to the
existing control supports. [Evidence01](evidence01/report.json) records original
catalogue rows, reviewed corrections, conditional section datums and photograph
limits. **This packet adds no physical CAD parts.** The mechanically feasible
[driver/bow study](../driver_layout_study/README.md) remains conditional context.

- [Seat section and shaft comparison](evidence01/seat_section_datums.png).
- [Original seat assembly list](evidence01/p207_seat_rows.png).
- [Corroborating bearing-rivet row](evidence01/p167_seat_rows.png).
- [Separate SH291C clip entry](evidence01/p066_seat_rows.png).

## Source-backed population and correction

SNL207:024–030 gives one M791 adjustable seat, four SH289E bearings, two SH291X
clips, twenty-one half-inch upholstering nails and eight bearing rivets.
**The original scan reads ⅜ × 1⅛-inch rivets, not the transcribed ⅝-inch diameter.**
Original SNL167:016 corroborates ⅜ × 1⅛ inch and two per bearing. The reviewed
9.525 mm diameter / 28.575 mm stock override is local and explicit; frozen source
transcription remains unchanged.

SNL66:006 separately lists one SH291C driver-seat clip, length 3½ inches. This
does not prove equivalence with the two SH291X clips. Retain all three identities
and their different counts as evidence; determine the C clip's application before
counting it within the adjustable-seat assembly or transferring its 88.9 mm length.

The two M788 support angles are listed at SNL5:006. SNL31:008 associates four
½ × 1⅝-inch bolts with each angle: eight 41.275 mm bolts, plain nuts and lock
washers. These differ from the eight 31.75 mm bolts already used on M786/M787.
M786/M787 support outlines and seat extensions are still incomplete, even though
their current shaft/floor mounting interfaces have passed mechanical checks.

## Shape and positioning evidence

The unchanged SNL2 section depicts the pan and curved back above the old
`layout_only` seat envelope. The provisional underside line at pixel Y339 gives
Z1517.638 mm and depth397.782 mm in the existing conditional calibration. It is
124.494 mm above the old envelope top and542.638 mm above the Z975 shaft hypothesis.
These are **drawing-derived construction estimates**, with 3–5 px pick uncertainty
plus unquantified source distortion/configuration error, not printed dimensions.
Source-picked curves cannot later be counted as independent validation points.

Original HB6 shows the curved back and support frame in perspective. It is useful
for topology but has no qualified camera or metric width measurement. HB14 says
the seated driver's head occupies the forward enclosure; HB146 describes seat
and forward controls as one assembly. Neither supplies a numerical seat height.
SNL7 is an armor assembly view and does not resolve hidden seat-bearing geometry.

Width, bearing bores/forms, clip profiles, adjustment axis and travel, support
attachment details and upholstery construction remain unmeasured. The visible
side-profile members are insufficient to assign every bearing and clip by sight.

## Next construction

1. Build a local M791 frame/pan/back prototype from the section profile and HB6
   topology. Use analytic stock and source-controlled spline sections where the
   curved shape warrants them. Record width and hidden structure as estimates.
2. Establish four real SH289E receiving interfaces and the two SH291X clips;
   preserve the reviewed rivet stock and distinguish the separate SH291C record.
3. Complete M786/M787 seat extensions and the two M788 angles with full hardware.
   Reconcile seat and shaft datums as one installation; do not inherit Z975 merely
   because that conditional mechanism clears the bow.
4. Check saved material, real contact and bores, full context, STEP, a relevant
   parameter variation and a fresh rebuild. Compare the source section with the
   current registration; treat HB6 as qualitative until a camera fit is supported.

Run `build_driver_seat_evidence.py --output NEW_PATH` with system Python to
reproduce the extracted source packet and views. Source hashes and exact image
crop transforms are in the report. Geometry/accepted progression remain unchanged.
