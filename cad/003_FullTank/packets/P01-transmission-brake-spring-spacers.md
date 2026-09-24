# P01 — transmission brake adjusting-spring spacers

Status: **local static checks passed; reviewed approximation**. Continue the standard
assembly, including interiors, before pose work. The four added SH687A occurrences
are identified by SNL218:013 and SNL252:026, survey `P_612e0e94ea39e728`.

Original SNL218 and252 were directly inspected. They establish the part mark and
four installed pieces. SNL218 prints `W. I., 1″ x 1¼″` without explicitly naming
diameter, length or bore. Original handbook page156 describes the adjusting spring
between the brake lever and a shoulder on the adjusting screw. HB101/102/134 show
the surrounding mechanism but do not separately identify SH687A. The retained
[source packet](../experiments/drive_chains/transmission_brake_spacer_study/sources.json)
separates literal evidence from the chosen geometry.

The current hypothesis is a 25.4 mm outside-diameter, 31.75 mm long annulus at the
swivel end of each spring. Its 13.0 mm bore clears the retained estimated 12.7 mm
screw by 0.15 mm radially. Assignment of the two stock dimensions, the bore and the
swivel-side position are explicit approximations. Shoulder-side placement, another
stock convention or a configuration difference remain alternatives. This is not a
claim that the catalogue specifies nominal pipe dimensions.

The saved parent spring already fills the space from shoulder to swivel. The
candidate therefore shortens its estimated installed length from 112.823802 to
81.073802 mm while retaining its shoulder-side origin, estimated wire/radius/turn
count, and all screw, swivel, lever, nut and pin geometry and placements. Each
spacer belongs to the same existing front-mechanism assembly as its spring. One
shared spacer definition serves four occurrences; one shared spring definition is
revised. The candidate contains 3,005 physical occurrences, 504 definitions and 295
assemblies. The standard tank011 assembly has not yet been updated.

The first saved candidate passes 321 local checks, including the 295 assembly
membership/frame checks, and 28 development-neighbor pairs. Actual planar bearing
areas are approximately 44.00 mm² at shoulder/spring, 44.32 mm² at spring/spacer,
373.98 mm² at spacer/swivel and181.43 mm² at swivel/nut. A displaced spacer loses
the spring seat; a blocked-bore control fails the void criterion. These establish
local static fit, not historical placement or service access.

The fixed-channel HB134 overlay retains the earlier mismatch around the screw and
swivel. It is a diagnostic comparison to a pictorial section, not a calibrated
photograph or evidence that the unlabelled spacer occupies the drawn location.
No camera refit was used to improve its apparent agreement.

All 13 deterministic stages pass. Preservation covers all 502 unchanged inherited
definitions (473 identical BRep bytes, 29 strict material comparisons). All ten
STEP comparisons pass for the two new/revised definitions and eight installed
occurrences. The retained 5,316-component standard context has no nearby affected
pair. Fresh reproduction matches 1,540 archived BReps and 140,153 persistent
properties. Increasing spacer length by 1 mm and bore radius by 0.25 mm shortens
the spring by 1 mm, moves only the four spacers, preserves the other 502 definitions
and passes the same native checks. This tests sensitivity, not historical stock.

[Trial01 qualification](../experiments/drive_chains/transmission_brake_spacer_study/trial01/qualification.json)
binds the native and saved receipts. Its three reviewed snapshots bring the visual
progression to 199; all 196 previous images are preserved. The decision ledger
permits reuse within local static development. Historical accuracy and full
service/installation remain open. Complete high-speed brake assemblies and their
controls are next.

Reopen the interpretation for a newly identified spacer drawing, a source that
explains the stock notation, a configuration conflict, or a changed screw/spring/
swivel interface. Keep the inherited brake-stop identity and service-path issues
visible; this packet does not settle them.
