# Front-hull rake contradiction

**The saved central front plate slopes the opposite way from the source wall.**
This is visible in the [native/source overlay](front_hull_audit.png) and the
[unretouched original-scan crop](original_front_crop.png). Neither the model nor
the existing whole-tank `snl_2` registration was changed for the comparison.

| Front-wall endpoints in SNL2 pixels | Lower | Upper |
| --- | --- | --- |
| Saved plate's largest planar face | (442, 421) | (345.47, 237) |
| Reviewed source central wall | (316, 392) | (404, 240) |

Positive vehicle X points left on this image. The saved plate therefore rises
forward at 61.93 degrees in world XZ, while the source line rises aft at 120.48
degrees. The sign difference is much larger than the 5 px endpoint allowance.
The reviewed source is the central sloping wall, not the outer track-frame cheek.
The high-resolution original scan confirms its orientation independently of the
processed image's display.

The current `hull_parts.py` constructs `front_slope` from image point (442,421),
also used for the first floor station, to the derived driver-enclosure front at
roof height. The upper enclosure uses separately interpreted handbook dimensions
and a traced base datum; its front also differs from the section. The red plate,
purple enclosure and grey floors in the overlay expose the coupled problem.

**Correcting this wall alone is not a demonstrated solution.** Under the existing
conditional whole-tank registration, current grip poles lie about 111 mm beyond
the reviewed source wall plane; the source-direction functional-radius trial is
about 219 mm beyond it. These are point-to-plane diagnostics, not a substituted
solid or an installation acceptance. The control state and whole-figure component
scaling remain uncertain. Neither a literal tracing nor an arbitrary module
translation is justified by this audit alone.

Next reconstruct the bow wall and lower floor junction, review HB35/HB43 enclosure
dimension identities and SNL2/SNL7/HB6 context, and verify the plate identity and
roof joins. Reassess driver and seat/support placement against those physical
surfaces and the complete source-length rods. Then revisit the handle profile
and static control state. Preserve the previous models as diagnostic checkpoints;
do not use their known contradictory bow surface as unquestioned historical
ground truth.

The [report](report.json) binds the saved native, standard hull BRep, old
calibration, authored parameters/datums, original scan, source picks and worker.
This audit is evidence of a required reconstruction correction. It is not a
qualified replacement hull, a new camera fit, or completion of the driver station.
