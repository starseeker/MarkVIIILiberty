"""Propose STEP solid pairings using cached mass-property signatures.

This preserves the project's existing nearest-signature rule. It is only a
pair selector: callers must independently check topology, both material
differences, tolerances and converged mass properties before accepting a pair.
"""


class StepSolidMatcher:
    def __init__(self, solids):
        self.available = [
            (index, solid, solid.CenterOfMass, solid.Volume)
            for index, solid in enumerate(solids)
        ]

    def pop(self, native):
        if len(native.Solids) != 1:
            raise ValueError('Pair matching requires one native solid')
        if not self.available:
            raise ValueError('No unmatched STEP solids remain')
        centroid = native.Solids[0].CenterOfMass
        volume = native.Volume
        position, selected = min(
            enumerate(self.available),
            key=lambda pair: (pair[1][2] - centroid).Length
            + abs(pair[1][3] - volume) / max(volume, 1),
        )
        self.available.pop(position)
        return selected[0], selected[1]

    def __len__(self):
        return len(self.available)
