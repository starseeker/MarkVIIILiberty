# Revised receiver topology naming

The first integration checker passed all shape transfers and frames but rejected
one persistent Shape-property difference on `ReconstructedFrontBrakePart006`,
the existing tip of the intentionally rebuilt `Def_BrakeFront_lever` (M330).
The native Shape property gained `HasherIndex=0`, an ElementMap dummy entry and
an ElementMap2 archive reference. Its BRep file reference is unchanged. The
original checker and failed receipt are retained beside this note.

The parent XML contains no LinkSub reference to that body or tip. The revised
checker permits Shape naming metadata only for tips of the two explicitly
revised receiver bodies, requires the same property type and BRep file reference,
and retains strict complete material comparison against the reviewed prototype.
All other inherited persistent properties keep the original checks. Native
geometry and acceptance tolerances were not changed for this checker correction.
