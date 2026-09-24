# Track-lug STEP tolerance diagnostic

FreeCAD 1.1.1 / Open CASCADE 7.8.0, 24 September 2026.

The initial flat compound exports passed 86 of 89 strict comparisons. The track
lug and both installed copies matched material in both directions and had
converged adaptive centroids, but their STEP maximum tolerance increased from
2.34996733e-7 mm to approximately 2.3959e-7 mm. The initial files, checker and
failed receipt are retained under `initial_flat_exchange/`.

`lug_step/` tests the original lug and an optional `removeSplitter()` applied to
a copy. Both pass individually at the definition, port and starboard poses. The
original remains unmodified. Cleanup provides no useful improvement here and
is not incorporated in the builder.

`step_assembly/` retains the 13-definition combined control. Setting
`write.step.assembly` to either 0 or 1 before `TopoShape.exportStep()` still
produces one uncertainty context and no assembly-use entities in this local
wrapper. The same track-lug failure persists. This is an observation about the
tested wrapper, not a general claim that the OCCT assembly option is ineffective.

`step_products/` exports the same 13 saved definitions as individually named
`PartDesign::Feature` objects through headless `Import.export()`. The resulting
file has 13 component uses and 14 uncertainty contexts. All 13 material/tolerance
comparisons pass; the track lug reopens at about 1.2343e-7 mm. No native shape,
read-tolerance setting or acceptance limit is altered. The main exchange checker
now tests this representation for all 89 definition/installed pairs, including
converged mass measurements. Its final receipt determines full exchange status.

The combined file records 2e-7 mm uncertainty, while the isolated lug records
1e-7 mm. These observations are consistent with OCCT's documented default of
deriving export uncertainty from average shape tolerance and using the recorded
uncertainty during reading. See the official
[STEP translator documentation](https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html#occt_step_2_3_2).
This interpretation does not claim a general geometric repair or artificially
increase certainty about the historical part.

The retained probe scripts were run from `.work/transmission-brake-stops/` and
resolve the repository from that location. To replay a probe, copy its `.py`
file to that directory and launch it with the project's headless FreeCAD helper.
The probes write their named diagnostic directories; preserve existing evidence
before an intentional replay. The frozen main exchange checker records the
separate full validation, with unchanged material and tolerance thresholds.
