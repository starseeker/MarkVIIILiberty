# Superseded: SNL end-retention identity error

The first 1,548-leaf candidate passed its static geometry checks but assigned
SH861E to the large bearing-end collar. The full rotated SNL Plate21 callout
trace disproves that identity: callout28 points to SH998B thrust collar, while
callout30 points to a separate external snap ring on the sliding collar.

This preserved candidate is NOT an accepted parent for continued construction.
Its earlier qualification receipt predates this source correction. Commit
f78ba521b249f1d6ccfee4a33c763b05936a0cd9 preserves the original state.
The revised candidate returns to the 1,540-leaf collar-joint parent, adds the
thrust collar and a separate external ring with corrected receiving geometry,
and removes the unsupported internal snap-ring groove. No frozen survey rows
or original source images are altered.
