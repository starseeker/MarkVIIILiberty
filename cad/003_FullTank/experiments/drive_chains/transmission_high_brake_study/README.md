# High-speed brake reconstruction in progress

The target is two complete brake assemblies, each with long and short bands,
linings, anchor end/pin/bracket, the paired-member lever, adjustment screw/nut/
spring/washers, three stops and all identified hardware. Controls connect to the
lever later. Existing high-speed drums are retained.

The source inventory records the original figure and catalogue reviews before
geometry construction. SNL119 supplies 1⅞-inch width and ¼-inch lining stock,
27⅜-inch long MX109 strips and 13⅝-inch short M364 strips, two of each. HB99 gives
the short strip's radius and six staggered holes. Its section's two ⅛-inch
thickness dimensions agree with the catalogue's ¼-inch stock; the 35-degree
half-angle gives a 70-degree countersink. Repeating the six-hole pattern for the
long strip is an explicit inference, with the extra ⅛-inch length between groups.

HB lists six M364 linings and repeats that mark around its assembled drawing;
SNL specifies two long plus two short pieces. This packet selects the SNL
continuous-long variant, without asserting an alias or the date of a design
change. HB100, HB133 and SNL30 repeat one illustration; they are not independent
views. They are pictorial sections with local depth, not calibrated photographs.
No perspective camera has been fitted to them.

The saved drum face is 46.445714 mm wide, from an earlier image-derived station;
the printed lining is 47.625 mm wide. A centered strip overhangs by 0.589643 mm
on each edge, leaving 97.52% axial coverage. Keep this explicit when checking
bearing surfaces; do not silently widen the old drum.

The initial 3/16-inch estimated steel backing intersects the retained case's
rear wall by 2,593.34 mm³ on each side. Shifting it outboard does not cure this:
the wall extends across the band width. Both failed trials are retained in
[diagnostics](diagnostics). The current trial uses an estimated 3/32-inch backing,
retains the centered datum and printed lining stock, and has no detected material
intersection in the pre-assembly probe. Thin steel is consistent with the drawn
flexible strap, but the exact thickness is not printed. These are fit-informed
approximations, not newly established historical dimensions.

`build_transmission_high_brake_bands.py` creates eight preliminary leaves and
seven owned groups. It deliberately identifies the backings as partial: ears,
anchor fittings, their holes and all fasteners still need construction. The
four-stage `high_brake_band_development.json` plan saves, reopens, checks and
renders this intermediate. It does not include full preservation, STEP,
reproduction or parameter qualification. No full assembly or standard tank
promotion is implied.

Continue by resolving the end-ear and anchor geometry in HB100/133 and catalogue
composition. Each lever assembly includes both M355A and M355B and four rivets.
Keep the two washer IDs/different bores, short-band brass screw, long/short copper
rivet stock lengths, six steel anchor rivets and the three stop adjusters per side
separate. Recheck the inherited frame/central-case receivers and actual bearing
faces as these fittings become concrete. Finish independent checks, exchange,
preservation, parameter/rebuild qualification and source comparisons before
integrating into standard tank011. Poses remain deferred.
