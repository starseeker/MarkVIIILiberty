# SH687A transmission brake adjusting-spring spacers

[Trial01](trial01/README.md) adds four source-identified spacers with an explicitly
estimated form and position. It passes local static, STEP, preservation,
reproduction and parameter checks. See the
[work packet](../../../packets/P01-transmission-brake-spring-spacers.md) and
[source distinctions](sources.json).

The saved parent spring filled the shoulder-to-swivel gap. The chosen annulus
shortens its estimated installed length from 112.823802 to 81.073802 mm;
other mechanism geometry and frames remain fixed. Catalogue stock notation does
not prove the chosen diameter/length roles, bore or swivel-side position.

The earlier [context audit](context.json) uses optimal trimmed-surface bounds and
restricts the swivel to the spring-radius cylinder. Ordinary broad BRep bounds
had overstated spring length; that initial diagnostic remains in
`.work/brake-spacer/initial_broad_bounds.json`. Trial01 now checks actual annular
contacts and independent voids, beyond the preparation's axial occupancy audit.

The original HB134 pictorial-section registration is retained. No camera refit or
standard tank011 update was made. Continue with complete high-speed brake bands,
anchors, adjusters, stops and hardware before full controls and tank integration.
