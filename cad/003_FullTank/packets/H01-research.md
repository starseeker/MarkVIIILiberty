# H01 evidence prepared during the track-unit build

This is a research handoff for hull plate construction, not an accepted geometry
packet. No hull component geometry is claimed by these notes.

HB pp. 35–41 were read directly from the frozen survey transcription. Page 35
specifies 12 mm hull side plates, 16 mm rear gasoline-compartment backplate,
10 mm front wing and outside skirting plates, 12 mm front diaphragm, 16 mm
main-enclosure side plates, 6 mm main/driver/lookout roofs and 16 mm lookout sides.
These transfer provisionally to the selected production configuration.

HB pp. 36–38 describe the hull as an H in plan: central body, with projecting
track-frame sides. Sponsons swing aft about their forward hinges after rear
flange bolts are removed. The support roller is 110 mm OD, 40 mm bore and 27 mm
wide; its track is a 3/4 in × 4 in bar on an arc centered at the hinge, with three
floor brackets. These are useful later pose constraints, not a license to choose
an arbitrary swing center.

HB p. 39 gives side doors 28.5 in × 41.875 in and a top door 20 in longitudinally
× 15.875 in transversely. HB p. 40 gives intake opening 37.25 in wide × 25.825 in
long and outlet 37.25 in wide × 37.625 in long. It lists 34 inlet and 29 outlet
6 mm angle-bent blades, 2.5 in extreme width, 0.5 in bend radius and 122 distance
pieces across both louvers. These counts must be reconciled with the individual
SNL assemblies before instantiating them. HB p. 41 puts 6 mm flanged guards
8.75 in above the hull roof.

## Identified source families

Query `part_identifiers` joined to `parts` using the following original piece
marks; suffixes matter. Handbook unsuffixed identities and SNL handed identities
must not be summed as different installed pieces.

| Family | Piece marks and useful distinctions |
|---|---|
| Roof | M1901A/B front wings; M1902 over driver; M1903 aft of upper enclosure; M1904A rear under right track; M1905 before inlet louver; M1908 removable engine plate; M1909A behind inlet; M1911 gasoline roof; M1912A beside outlet; M1915A rear under left track; M1917 rear under track; M1914/M1918 mud-chute-adjacent roof |
| Floor | M1931–M1938 numbered floor plates 1–8; M1939 below gasoline tank; M1949 floor inspection cover |
| Forward wing | M1961A/B lower outside; M1962A/B upper outside; M1963A/B outside forward of sponsons; M1964A/B front inside upper; M2093/M2094 front wing inside upper/lower |
| Fighting compartment | M1965/M1966 below sponsons; M1967A/B above doors; M1968A/B beside doors; M1969 below doors; M1970A/B aft of sponsons; M1992 above sponsons |
| Engine compartment | M1971A/B No.1 sides; M1973 left No.2; M2070 right No.2; M1990 No.3; M1991 left removable; M2077 right removable; M2003 back |
| Rear wings/fuel | M1975A/B outside back; M1976A/B outside rear; M1977 inside beside fuel; M1978 rear inside; M1979 cover behind mud chute; M2021 back |
| Skirting | M1983A/B inside front/rear halves; M1984/M1985 outside front/rear halves |
| Chutes | M1986/M1987 front chute sides; M1988 bottom; M1989A/B back; M2028 above rear chute; M2095/M2096 rear vertical/sloping sides |
| Sloping/front | M2014/M2033 front sloping; M2038 front diaphragm; M2073 below driver; M2097/M2098 upper/lower sloping |
| Bulkhead | M2137 top; M2138 center; M2139 bottom; M2140 sides; nearby angles/stiffeners have separate identities |

Examples retained for lookup:

- M1931: P_5d97409e5c341fd4; M1932: P_74193e7111f07b92.
- M1971A: P_c4cc68346b5bc783; M1971B: P_70ef962f5fbec5da.
- M1973: P_5c7c37b8a379bbcf; M2070: P_ce19d06cc015f76c.
- M1983A: P_0619a3d907241500; M1983B: P_8da757ab98b628be.
- M1984: P_c04b9dba08c580f6; M1985: P_c150ff4d004aa47b.

SNL:148:009 locates M1971B on Plate7. Inspect that exact figure and neighboring
plate callouts, plus the longitudinal foldout and held-out views, before assigning
panel boundaries. The current track-frame and central-hull envelopes are context
only. Their inferred widths must be reconciled with the handbook's 22.25 in
inside/outside track-frame plate spacing before becoming mating plate planes.

## Follow-up source inspection — 19 September 2026

Inspected the original SNL Plate 7 geometry image at
`references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p281-geometry.png`.
It is an oblique assembled armor view, useful for panel identities and seam
relationships; it is not an orthographic metric calibration. It distinguishes
No.1/No.2 engine-side panels, removable rear panels, skirting and roof strips.
Do not assign their complete outlines from the longitudinal cutaway alone.

SNL148:009 identifies M1971B, left No.1 engine-room side plate, quantity (1);
SNL148:010 identifies M1971A, right No.1 engine-room side plate, quantity (1).
The two handed definitions must remain distinct until their openings and edge
geometry have been compared. The catalogue quantity notation retains its source
scope; the apparent left/right pair is not an automatic general BOM summation.

HB141 gives 22.25 in between the inner and outer shell plates along the lower
roller line. This is a stronger transverse constraint than the current
shoe-width-derived central envelope. Establish the four plate face datums from
that gap, documented thickness and the track centers before installing the
roller shafts or claiming the engine-side panel interfaces are correct.

Also inspected HB32 (side of hull) and HB30 (top of hull). HB32 shows the
side-door hinge strips, its circular mount opening, a neighboring large opening
and the surrounding riveted panel seams. HB30 shows the roof hatch, lookout
panels, roof seams and the upper enclosure end opening. These oblique photographs
support feature and seam interpretation; they do not supply a uniform metric
scale. Combine them with SNL7 and fixed SNL2 longitudinal controls, retaining
bounded stations and handedness until the source relationships are resolved.

The side access doors are split components: M702/M704 are port upper/lower,
and M703/M705 are starboard upper/lower. M704 is not an entire door panel.
Likewise the roof hatch has two handed plates M2355/M2356. Apply HB39's stated
door/opening dimensions at the combined-door scope until the split and overlap
are established. See [P02 preparation](P02-research.md) for the located identities
and the selected static pose requirements.

## Additional controlling dimensions for the standard hull

HB11 places the engine room over 9 ft 9 in longitudinally and gives 4 ft 8.125 in
from its rear to the track-drive center. HB12 describes the bulkhead and the
extended side structures enclosing the chain drive aft and adjuster forward.
These are independent station controls to compare with the SNL2 picks.

HB43 adds dimensions that must be reconciled with HB39 **before sizing the
standard closed doors**. It gives side-hull door openings 29.875 × 59.875 in,
while HB39 calls the side doors 28.5 × 41.875 in. The identified upper/lower
pieces suggest that the smaller height might describe the upper section, but
that is an interpretation to check against the source figures, not a settled
dimension. Do not assign either pair blindly to every door piece.

For the roof, HB43 describes two upward-opening leaves, each 21.5 × 8.875 in;
HB39 gives a 20 × 15.875 in top opening/door. Leaf versus clear-opening scope
could explain this difference, but overlap and mounting margins still need
explicit reconstruction.

HB43 also identifies upper-enclosure side doors as 16.812 × 15.812 in, a rear
pistol opening 3.5 × 2.5 in and a rear peephole 1 × 4.25 in. These dimensions
provide standard-panel opening controls. All closure geometry is to be built in
its normal closed installation first; alternative placements are deferred.

## Next standard-geometry pass after S01 upper shells

S01 now supplies actual upper enclosure plates; the central hull and both track
frames remain reference envelopes. Before promoting the lower shell, resolve the
transverse planes explicitly. HB141 gives 22.25 in (565.15 mm) between inside and
outside shells, while HB9 gives track centers 69.5 in (1,765.3 mm). If that clear
space is centered on the shoe centerline, the inner roller-facing planes would
be at Y = ±600.075 mm. With provisional 12 mm inner shell thickness, the
fighting-space faces would be at Y = ±588.075 mm, a 1,176.15 mm clear body width.
This is a derived candidate, not an adopted datum: verify what the handbook's
clearance measures, whether the shoe center bisects it, and which local plates
are 12 mm rather than the 10 mm skirts/front wings. The present layout's
shoe-edge gap is not an interchangeable hull width.

Use the SNL7 seam and piece-mark map with longitudinal profile SNL2, preserve
source conflicts, and populate floor/roof/side plates in source-identified sets.
Model closed standard side doors and service covers with the shell; their
identifiable hardware follows before any alternative poses.
