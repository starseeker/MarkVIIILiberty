# Cache unchanged matching inputs

The former screen matcher recomputed OCC volume and area inside each candidate
comparison. The revised matcher evaluates the same properties once per unchanged
solid. Both runs cover the same 186 pairs; [the comparison](equivalence.json)
confirms identical pair results, hashes, negative controls and coverage. Exact
native/STEP BRep matching, identity poses and unit link scale remain mandatory.
This is a computation change, not a relaxed geometry criterion.
