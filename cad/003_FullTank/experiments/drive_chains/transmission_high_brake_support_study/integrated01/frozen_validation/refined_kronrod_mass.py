"""Explicit tighter integration after diagnosed whole-case convergence failure.

Keep the original validity, reported-error and absolute convergence predicates.
Only the two requested quadrature precisions change, both becoming tighter.
The default adapter and its qualified clients remain unchanged.
"""
from pathlib import Path
import subprocess
from .kronrod_mass import KronrodMass
from .mass_properties import digest


class RefinedKronrodMass(KronrodMass):
    def __init__(self, work, freecad_root=Path('/snap/freecad/current')):
        super().__init__(work, freecad_root)
        baseline = dict(self.provenance)
        original = Path(__file__).with_name('occt_kronrod_mass.cpp')
        text = original.read_text()
        assert text.count('{1e-10,1e-12}') == 1
        source = self.work/'occt_kronrod_mass_refined.cpp'
        source.write_text(text.replace('{1e-10,1e-12}', '{1e-12,1e-13}'))
        self.binary = self.work/'occt_kronrod_mass_refined'
        command = baseline['compile_command'][:]
        command[command.index(str(original))] = str(source)
        command[-1] = str(self.binary)
        subprocess.run(command, env=self.environment, check=True, capture_output=True, text=True)
        self.provenance = dict(adapter_sha256=digest(Path(__file__)),
            baseline_provenance=baseline, source_sha256=digest(source),
            binary_sha256=digest(self.binary), compile_command=command,
            requested_errors=[1e-12,1e-13], acceptance_predicates='Unchanged AdaptiveMass.measure',
            purpose='Explicit diagnostic refinement; does not alter CAD geometry or default integration settings.')
