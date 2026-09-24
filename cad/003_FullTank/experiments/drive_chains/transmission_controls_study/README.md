# Transmission operating controls — evidence and receiving interfaces

Current assembly: [PowertrainWithRearTrackJoints.FCStd](track_joints_integrated01/PowertrainWithRearTrackJoints.FCStd),
with **3,262 physical occurrences / 567 used definitions / 359 assembly groups**.
The [track-joint checkpoint](track_joints_integrated01/README.md) adds four M569C
forks and their pins, cotters and shared plain nuts in two short-connection groups.
The [preceding support-family checkpoint](support_integrated01/README.md) installed
M4135, M4136 and estimated M4129 attachments. Actual rods, final fork angles,
return springs and complete service paths remain open. SNL136's shared M568A
application exposes a15.875mm pin versus13mm low-speed-eye conflict; resolve the
existing estimates before constructing M569A joints.
The [fulcrum checkpoint](fulcrum_integrated01/README.md) follows the
[channel mounting checkpoint](channel_integrated01/README.md), the
[rear-joint checkpoint](us_nuts01/README.md) and the locally qualified
[brake-support assembly](../transmission_high_brake_support_study/integrated_upper01/qualification.json).
This packet covers the rear control channel, brake return springs, control rod
ends and subsequent connections toward the center and driver controls. Two rear high-speed fork/pin/cotter joints and their plain nuts are now installed.
The channel, four M4130 mounting sets and four retained M4131/lever units are
installed in the development assembly. M4135/M4136 and estimated M4129 attachments
added20 parts in the preceding checkpoint; four track end joints now add16 more. Rods and return springs remain pending.
The preceding fulcrum units added24 physical occurrences:
four brackets, four levers, four washers, four cotters and eight rivets.

The fulcrum checkpoint retains an earlier geometry hypothesis and the source
review that led to the revised bearing column. Native/interface/context/STEP
checks pass in nominal and thicker-boss variants; actual prototype geometry
transfers into the full development hierarchy. Its source overlay reuses the
unchanged local SNL6 registration and preserves the existing control-bore
discrepancy. Four new images bring visual progression to 229.

The [M4136 shared spring-support study](low_spring04/README.md) now adds a second
locally checked seven-occurrence prototype. Nominal and thicker stock pass
native/interface/context/STEP checks and provisional rod/spring corridor checks.
The raised ends address retained lever interference and a source-height mismatch;
remaining spring inclination and endpoint differences stay explicit. Both support
studies were subsequently installed by the support-family checkpoint. Three more views bring progression
to 235, preserving the earlier images and fixed camera.

The [M4135 guide study](high_spring04/README.md) now has two locally checked
brackets, four rivets and local rod/spring clearance witnesses. This seven-part
prototype records the earlier isolated study; its support geometry is now integrated. Nominal and
thicker stock pass native/interface/context/STEP checks. Three new reviewed images
bring progression to 232, preserving earlier views and the unchanged source camera.

**Source identity correction:** the four short connections in the
[saved interface measurements](fulcrum_integrated01/operating_interfaces.json)
are SH946D (track, M569C forks) and SH946E (low-speed, M569A forks), functionally
corresponding to handbook M577 and M572. Their coordinates and perpendicular end
pin axes remain valid. M578/M573 identify the longer rear rods to the center
controls. The additive [source packet](spring_sources01/sources.json) preserves
the correction and original evidence; the old receipt remains immutable.
Endpoint chords do not establish clear routes or finished rod lengths.

[sources.json](sources.json) retains 99 source rows associated with 34 identities,
handbook operating/adjustment text, literal dimensional constraints and source
hashes. The original [native identity audit](inventory_audit.json) found no matching
definitions in the brake-support parent. It is retained as an input checkpoint;
new fork/pin/cotter identities are checked in [the integrated catalogue audit](integrated01/catalogue_checks.json).
Unmarked generic parts can escape the original audit, so check physical ownership
again before subsequent integration. The evidence and
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

## Rear high-speed joints now populated

M569B is provisionally assigned to the wider brake ends of M575. The selected
38.1mm fork length is measured from pin center to socket face, giving21.6mm of
threaded socket. Treating38.1mm as overall length leaves7.3125mm with the same
throat/profile, which fails the chosen one-diameter engagement criterion. This
comparison does not prove the historical datum. M568A uses the physical-row
41.275mm length with an assumed underhead datum; the47.625mm aggregate conflict
remains open. See [the reviewed alternatives](joint01/visual_review.json).

The first joint trial reused a smaller3/4inch nut. A subsequent
[period-standard review](us_standard_nut_review.json) selected a separate classic
U.S. Standard nut envelope,31.75mm across flats and19.05mm thick. Catalogue wording
may specify thread series without fixing the outside finish, so that choice
remains provisional. The existing clutch nut definition is preserved for its
original applications; it should be reviewed against those sources separately.

Both fork stock variants pass saved material and STEP checks. The larger nuts
also fit the thicker-ear variation. The old small-nut trial and its images remain
visible evidence of the correction. All thread geometry is a nominal cylindrical
envelope; parameter edits require regenerating the scripted part model.

## Next construction

The [rear-channel stock study](channel_stock01/README.md) established a
conditional local SNL6 registration, measured floor context and a separately
saved downward-open channel prototype. Two stock variants pass local native,
floor/material and STEP checks. The subsequent
[mounted increment](channel_integrated01/README.md) installs four M4130 cleats,
four floor bolt sets and twelve rivets with receiving holes. It preserves the
first interfering foot layout and tests a revised estimated profile in two stock
thicknesses. The preserved 21.867-pixel control-bore discrepancy calls for targeted
lever/rod review without changing the registration.

1. Establish M4129 attachment topology, M4131 fulcrum stations and M4135/M4136
   spring brackets on the mounted M4128. Check the narrow left clutch-support
   clearance before adding top rivets, and retain conflicting source counts.
2. Reconstruct M575 rear rod bends and spring interfaces between fixed endpoints,
   then connect the center rods. Revisit the estimated-12degree rear fork pitch
   if the complete route warrants it. Avoid scaling across drawn length breaks.
3. Develop the other rear control joints, retaining their specific fork/pin
   variants rather than scaling the high-speed fork indiscriminately.
4. Verify material, bearing/retention, neighboring routes, native/STEP export,
   parameter changes and source views before integrating each increment.
5. Continue center/front controls and remaining tank interiors, then complete
   standard-tank integration. Pose variants remain deferred.
