# Native link-placement serialization

Saving the unchanged180-degree mount fasteners normalized quaternion Q3 from0 to1e-16 for12 LinkPlacement properties. Their translations and other quaternion components are unchanged. All actual world frames, link targets, owners and material-transfer checks passed.

The first persistent-property auditor already allowed numerical serialization differences up to1e-12 for Placement but omitted the equivalent LinkPlacement property. The corrected auditor applies the same bound and exact XML structure to both. No native geometry was changed and no existing placement/material tolerance was enlarged. The initial checker, failure and individual property diffs are retained.
