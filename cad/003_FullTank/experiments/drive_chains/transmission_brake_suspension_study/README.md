# Transmission brake suspension study

The current candidate is [trial02](trial02/README.md): four identified M338
brackets and two M385 stops, with documented approximate profiles and incomplete
fastening. It continues the qualified frame-joint assembly without changing any
inherited part geometry or occurrence placement.

`trial01` registered the bracket pin longitudinally to the top channel. Its
saved-shape checks found four clashes: the two low-speed brackets intersected
the middle diaphragm and the two track-brake feet intersected the stops. Its
reports, frozen inputs, failed checker and review images are retained. The full
failed native remains locally available but is not part of the scoped checkpoint.

`trial02` locates the bracket pins from the shaft and the source pin-to-shaft
separation. All four brackets move forward 9.575922 mm relative to the rejected
layout; their upper faces remain on the retained channel. This resolves the
material clashes without changing the acceptance criteria. The datum conflict
remains visible in the source overlays and does not establish historical accuracy.

`sources.json` records source identities, counts and inspected figure hashes.
`controls.json` separates chosen profiles, conditional registration and estimated
thicknesses. `check_source_axis.py` independently fits the source opening to check
the manual shaft-center pick; its result agrees within the recorded four-pixel
allowance. It does not qualify the other picks or remove drawing/model disagreement.

Older trials freeze different input versions. Restore the relevant frozen inputs
to their repository-relative locations in a separate checkout to reproduce them.
The active builders expect the current controls and the qualified frame-joint
parent. No physical pose variant is introduced.
