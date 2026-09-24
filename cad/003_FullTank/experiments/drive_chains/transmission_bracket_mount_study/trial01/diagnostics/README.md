# Retained diagnostics

- `initial_check`: terminal failure of the original checker. It omitted the
  new definition-library children and used a rectangular witness covering an
  intentionally altered part of the casting web. All measured context pairs
  passed; the native model was not edited in response.
- `revised_check_failure`: terminal failure of the next checker. Its narrowed
  rectangular witness still included 642.996876 mm³ of revised web. The subsequent
  chained difference raised `ValueError: Null shape`. The copied final report
  is the **older** failed run; the partial progress file and log describe this run.
- `material_probe`: BReps locate the witness loss at Y ±10 mm, outside the named
  bearing region. All of it belongs to the declared web revision. The functional
  annulus/backbone and four stud lugs are preserved. Union-based whole-casting
  differences return zero extra/missing material, while deliberately damaged
  bearing material is detected. Sequential cuts failed even while the remainder
  reported valid solids; no claim is made that every such failure means an empty
  result. The original workstation probes retain their `.work` paths as run.
  The final portable checker implements and repeats the successful measurements.
- `initial_review` and `second_review`: the original cameras used vehicle Z as
  image-up and the selected photo geometry omitted the input housing. These views
  did not reproduce the photographed orientation. The final renderer includes
  that housing and uses vehicle X as image-up for this comparison only. Physical
  assembly placements are unchanged.
- `initial_reproduction`: all geometry, placements, hierarchy, BRep bytes and
  object types matched. The only property differences were generated UUIDs on the
  24 newly created assembly containers. The scoped checker validates those UUIDs
  and their uniqueness, while requiring inherited UUIDs and all other persistent
  properties to reproduce exactly.

These are superseded diagnostic outputs. Current qualified local results are the
reports at the trial root, bound by `validation_receipt.json`. Historical mounting
interpretation and complete installation remain unqualified.
