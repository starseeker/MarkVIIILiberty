# Retained crankshaft diagnostics

Each directory records a rejected development state, its inputs and diagnostic
results. These are not accepted verification results for the final candidate.

- Initial geometry: the gear flange intruded into the final main bearing. The
  initial distance check beside an oil hole needed correction, and a checker
  argument collision stopped material-pair testing.
- Detached flange: moving the flange without extending the neck produced two
  solids. The builder rejected the result before saving.
- Sleeve receiver: 420 independent checks passed, but 521 material pairs found
  18.895 mm³ of inherited lower-nose material inside the thrust sleeve. The final
  receiver cuts through original and added casting material; a 74 mm housing
  radius preserves 8.95 mm radial stock.
- Visual grooves: 421 checks and 521 material pairs passed, but source comparison
  rejected continuous inner grooves against Liberty figures 11 and 31. Local
  crossed channels and pockets replace them. Three rejected detail views remain.
- Groove unification and refinement mutation: valid bearing cuts became invalid
  after removeSplitter, which also mutated its input. The focused probe retains
  raw/refined BReps. Cleanup on a copy preserves the original and returns a valid
  result. The generator checks that result before selecting it.
- Spherical cage exchange: default-axis sphere pockets were valid natively but
  became invalid in STEP. Aligning the sphere axis with the trimming-plane normal
  passes both tested sizes in definition and installed frames without changing
  spherical material. The isolated probes retain these results.

The final cage bounds reduce the material-pair candidate count from 521 to 517.
A focused check confirms all four omitted pairs have positive separation and zero
overlap. Two initial probe assumptions (axial versus Euclidean distance, and
ordinary versus trimmed bounds) are corrected and retained in the probe history.

No numerical acceptance tolerance was relaxed. Earlier heavy native/STEP files
remain under .work/engine-crankshaft; diagnostic code, inputs, logs and relevant
receipts are retained here.
