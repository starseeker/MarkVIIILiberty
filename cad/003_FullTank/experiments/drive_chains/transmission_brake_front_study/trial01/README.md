# Front brake adjustment mechanisms — development trial

This saved candidate adds the front ears and adjustment mechanisms to the rear
brake-anchor checkpoint. **Native fit, STEP, preservation, reproduction and parameter checks pass.**
This is the next locally qualified powertrain development parent. It has not
been integrated into standard tank011.

`PowertrainWithBrakeFront.FCStd` contains 2,957 physical occurrences, 492 shared
physical definitions and 288 assembly groups. Eight `FrontEarJoint` groups own
the ears and foot rivets; four `FrontMechanism` groups own the adjusting parts
and retained pivots. A hidden, nonphysical spring centerline is retained in the
definition library. Parameters update by rerunning
`../../build_transmission_brake_front.py`; they are not live sketch constraints.

## Added and revised geometry

| Component | Installed quantity |
|---|---:|
| MX48 low-speed front ears | 4 |
| MX46 track-brake front ears | 4 |
| M336 free-end pins | 8 |
| Quarter-inch × 1½-inch cotters, one per M336 | 8 |
| Steel foot rivets, eight per MX48 and six per MX46 | 56 |
| M333 adjusting screws | 4 |
| M335 springs | 4 |
| M331 swivels | 4 |
| M332 adjusting nuts | 4 |
| M330 levers | 4 |

The 100 new occurrences use eight new definitions and three existing hardware
definitions. Two backing definitions gain the front rivet holes; 24 existing
copper rivets use the longer stock through the ear feet. Their old upset-head
pockets are filled. All inherited occurrence and assembly frames remain fixed.
Printed lining lengths, pitches, drum interfaces and the rear joints are preserved.

## Evidence and limitations

The source packet separates the M333 screw from M335 spring. Original handbook
page 207 prints M335 for both; the figure legends and SNL support M333 for the
screw. M336 has one source-listed split pin, whereas the previously modeled
M339 suspension pin has two. Catalogue quantities are not additional instances
of the same assembly.

The upper ear carries the screw; the lower ear carries the lever. A swivel in
the lever receives the screw, and the nut compresses the spring between the
swivel and screw shoulder. Paired lug widths, pivot and swivel sections, cast or
forged transitions, spring section/turn count and thread surfaces are estimates.
Threads are nominal cylindrical interfaces. No load rating, adjustment range,
spring elasticity or installation/removal sequence is claimed.

The first 24 mm pivot stand-off interfered with feet and rivet heads in 64
pairs. The selected estimated stand-off is 38 mm. It clears the complete saved
context while increasing the offset from the drawn pivot positions.
`source_review.json` retains manual picks and fixed channel registration for
HB134/135: the upper low-speed pivot is approximately 17.4 mm forward and
11.6 mm below the drawing; the track pivot is 16.0 mm forward and 37.6 mm below.
Those are conditional comparisons, not printed dimensions or proof of scan
error. Relative low-speed pin/swivel positions agree much more closely. The
global station residuals remain unresolved and visible in the overlays.

## Verification state

- All 119 saved-native checks pass, including complete foot support, holes,
  bearing contacts, pin retention, hierarchy and explicit negative controls.
- All 996 nearby development material pairs pass. The 5,316 retained standard
  occurrences produce no spatial candidate against the affected parts.
- All 482 unchanged inherited definitions are preserved: 456 exact BReps and
  26 strict material comparisons.
- Fresh reproduction matches all 1,504 archive BReps, 10,480 object types and
  137,434 persistent properties.
- A pin-height +2 mm / stand-off +2 mm rebuild passes all 119 native checks and
  context tests. Its STEP exchange has not been qualified.
- All 142 STEP comparisons pass. The 137 initial passes are retained unchanged;
  the five spring pairs pass a full geometric recheck and verified partitioned
  mass integration at the original tolerances.

`diagnostics/spring_mass/initial_exchange_checks.json` preserves the failure.
The alternative measurement partitions the unchanged solid into disjoint
slabs, requires every piece to meet the existing adaptive integration thresholds,
checks material coverage and overlap, and independently refines the partition.
It does not alter the exported geometry or relax the material/centroid limits.

Five views are saved in the project's visual progression, preserving all 183
earlier images. The new images show this in-progress candidate, not a completed
tank or a historically resolved brake assembly.

## Following work

Reconstruct the
stop lugs, stop screws and supports, control rods and high-speed brakes, followed
by remaining frame/hull fastenings, engine parts and all other selected interior
equipment. Reconcile inventory and integrate qualified development geometry
into the standard tank. Pose variants remain after standard geometry coverage.
