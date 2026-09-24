# Rear support-family prototype

This [22-occurrence native](RearSupportFamily.FCStd) combines two M4135 guides,
two M4136 spring supports, their eight rivets, two estimated M4129 cleats and
two complete bolt/lock-washer/nut sets. The other two occurrences are the
receiving channel and floor. Ten shared definitions supply the prototype.
The resulting installation is recorded in [support_integrated01](../support_integrated01/README.md).

Original SNL33 confirms one ¾ × 1⅝-inch bolt with plain nut and lock washer
per M4129; SNL65 and the channel aggregate specify two right cleats. M4130 uses
¾ × **2-inch** bolts. Plate21/callout25 points into the clutch figure despite
being printed against the M4129 bolt. The earlier clutch identity review already
records that conflict; it supplies no reliable M4129 outline or mounting datum.
See the [source review](../right_cleat_source_review01.json).

The selected **mounting hypothesis** places each right cleat on the forward face
of the channel. Its triangular foot bolts to the floor. A narrow neck reaches
a transverse pad above the channel roof and below the M4136 base, sharing that
support's two rivets. No separate M4129 rivet application has been identified;
that absence motivates testing a shared stack, but does not prove it.

Cleat stock is estimated at 9.525 mm. Each M4136 is lifted by that amount while
retaining its complete bracket shape. Its four mounting rivets retain the listed
12.7 mm diameter and 47.625 mm unformed stock, with a new 22.225 mm grip and
volume-conserving upset. A 10.025 mm cleat-stock variation also updates the
bracket lift, bolt seat and rivet grip. Outline, handedness, section, stations,
rivet-length datum and manufacturing method remain uncertain. Regenerate with
`trial_rear_support_family.py` and the corresponding controls JSON; metadata is
not a live geometric constraint.

Nominal and thicker stock each pass 67 saved-native/interface checks, 41 local
material comparisons, 20 surrounding-material comparisons and 32 strict STEP
comparisons. The checks cover full floor-foot/head bearing, reused nut/washer
contact, complete rivet bearing annuli, all three riveted layers, source stock,
bolt length and nut engagement, receiver material preservation and relocation.
STEP retains the existing material, tolerance and converged-mass thresholds.
The first checker mistakenly required a circular washer to bear completely on
a hex nut; its [failure and correction](diagnostics/washer_contact/README.md)
are retained. Geometry was unchanged, and a displaced-nut negative is required.

Both sets of eight provisional short-rod/spring witnesses pass 27 material
comparisons after the M4136 lift. They still exclude forks, washers and hooks;
they are not physical rods or springs. A fresh prototype generation reproduces
all 30 archive BReps, 1,836 persistent properties, frames and hierarchy, with
no allowed property differences.

The existing local SNL6 side camera is reused unchanged. It cannot establish the
hidden cleat stack. The spring-height/inclination disagreement remains visible,
and the separate 21.867-pixel high-speed control-bore discrepancy is retained.
New estimated cleat and anchor coordinates are not independent camera holdouts.
HB104 remains an uncalibrated photograph. Full historical shape, strength,
installation/service paths, complete controls and the standard tank are open.
