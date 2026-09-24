# Transmission operating controls — evidence and receiving interfaces

Continue from the locally qualified
[brake-support assembly](../transmission_high_brake_support_study/integrated_upper01/qualification.json).
This packet covers the rear control channel, brake return springs, control rod
ends and subsequent connections toward the center and driver controls. Geometry
for these identified control families has not yet been added.

[sources.json](sources.json) retains 99 source rows associated with 34 identities,
handbook operating/adjustment text, literal dimensional constraints and source
hashes. The [native identity audit](inventory_audit.json) finds no existing
matches for these selected identities. Unmarked generic parts can escape that
audit, so check physical ownership again before integration. The evidence and
audit reproduce byte for byte with `prepare_transmission_control_sources.py`.

## Receiving geometry

The [read-only native probe](context01/report.json) locates six control bores
from the saved cylindrical faces. All axes are transverse (world Y); the table
uses port Y, with starboard mirrored about Y=0. World coordinates are millimeters,
X forward, Y port, Z up. These measurements describe the current reconstruction,
not independently known historical dimensions.

| Joint | X | Port Y | Z | Bore diameter | Lever stock at joint |
|---|---:|---:|---:|---:|---:|
| High-speed brake | 2069.944642 | 222.25 | 606.927941 | 16.175 | 25.4 |
| Low-speed brake | 2150.175881 | 535.395714 | 610.602941 | 13.0 | 12.7 |
| Track brake | 2156.653867 | 770.164286 | 610.602941 | 13.0 | 12.7 |

The two high-speed lever members meet at the center plane: there is no slot
between them at the control eye. A proposed clevis must surround the complete
25.4 mm width. The [context view](context01/control_interfaces_isometric.png)
shows the retained levers and transmission structure. Missing bands and other
parts in this inspection view are display selection, not removed model geometry.

## Source constraints that affect construction

SNL195 identifies two M575 high-speed rear rods, each in an aggregate assembly
with two 3/4-inch jam nuts. SNL86 applies M569C to one end of each M575. SNL87
lists two M569B forks, length 1½ inches, and calls their application “band M575.”
That wording and its parenthetical quantity need an explicit interpretation;
do not silently rename the source or multiply the global quantity into four.
The likely one-C/one-B arrangement per rod remains a reconstruction hypothesis.
The 38.1 mm fork length has no explicit datum.

SNL136 distinguishes M568C pins (1 9/16 inches, applied to M569C/M570) from M568A
pins (1⅝ inches, applied to M569A/M569B, M565 and M771). Both list 1/8 × 1 inch
cotters. The aggregate control entry elsewhere calls M568A 1⅞ inches; retain
that conflict. Pin diameters and the stock-length datums are not printed here.
The existing model's bore estimates must not acquire historical certainty merely
because a matching pin can be constructed.

M4135 high-speed spring brackets belong to the M4128 rear control-channel
assembly (SNL63), together with four brake fulcrum assemblies and two M4136
low-speed/foot-brake spring brackets. Four 1/2 × 3/4 inch rivets are listed for
the two M4135 brackets. Thus the spring supports need a real receiving channel;
they cannot simply float beside the brake rods.

## Projection and reuse

HB92 and HB113 repeat a segmented plan/side layout. SNL Plate6 is a later labeled
version of that arrangement. Rod-length breaks prevent a single longitudinal
pixel scale from recovering overall rod length. Treat local segments and the
plan/side relationships separately; repeated drawings are not independent views.

HB104 is a separate photograph of the rod ends with the transmission removed.
It shows the rear control channel, forks and spring attachments, but no camera
has been calibrated. Use reviewed depth landmarks and independent holdouts if
fitting it becomes useful. HB12 shows the front control-shaft detail and must
not set the rear channel's scale. Existing HB133 brake registration remains valid
within its documented diagnostic scope.

## Next construction

1. Review M569B/M568A length datums and test a complete fork/pin/cotter/jam-nut
   joint against the saved high-speed eye. Preserve explicit source alternatives.
2. Locate M4128 and its cleats/brackets against the hull/floor and transmission
   structure. Establish the rear return-spring and low/track bell-crank axes.
3. Reconstruct M575 rear rod bends and spring interfaces between those fixed
   endpoints, then connect the center rods. Avoid scaling across drawn breaks.
4. Verify actual material, bearing/retention, neighboring routes, native/STEP
   export, parameter changes and source views before integrating each increment.
5. Continue the other rear controls and their connections to the existing clutch
   and transmission, then center/front controls and remaining tank interiors.

The full standard tank remains the priority. No pose variants or operating-motion
claims are introduced by this interface study.
