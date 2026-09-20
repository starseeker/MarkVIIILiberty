"""Reopen and check the experimental support installation; no delivery claims."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
sys.path.insert(0, str(STAGE))


def main():
    from lib.runtime import environment, close
    out = HERE / 'build'
    if '--worker' not in sys.argv:
        return subprocess.run([sys.executable, __file__, '--worker'], env=environment(out)).returncode
    # No GUI is needed for saved-solid and contact checks. Avoid tessellating
    # every baked context object just to verify native geometry.
    import FreeCAD as App
    try:
        from lib.evidence import read, write, sha
        from lib.roller_validation import bearing_face
        report = read(out / 'report.json')
        native = out / 'LowerSupportExperiment.FCStd'
        if sha(native) != report['native_file_sha256']:
            raise ValueError('Native experiment changed since collision report')
        if sha(HERE / 'probe.py') != report['experiment_script_sha256']:
            raise ValueError('Probe changed since native generation')
        if report['overlaps'] or report['missing_bearing_contacts'] or report['missing_bolt_contacts']:
            raise ValueError('Experiment still has unresolved native fit failures')
        doc = App.openDocument(str(native))
        print('REOPENED EXPERIMENT', flush=True)

        def shape(identifier, context=False):
            obj = doc.getObject(('Context_' if context else '') + identifier)
            if obj is None:
                raise ValueError('Missing reopened object: ' + identifier)
            if context:
                result = obj.Shape.copy()
            else:
                result = obj.LinkedObject.Shape.copy()
                bank = doc.getObject(identifier.split('_')[0])
                placement = doc.SupportExperiment.Placement.multiply(bank.Placement).multiply(obj.Placement)
                result.Placement = placement.multiply(result.Placement)
            if not result.isValid() or len(result.Solids) != 1:
                raise ValueError('Invalid reopened single solid: ' + identifier)
            return result

        supports = {r['id']: shape(r['id']) for r in report['runs']}
        bolts = {r['bolt']: shape(r['bolt']) for r in report['bolt_contacts']}
        if len(supports) != 34 or len(bolts) != 76:
            raise ValueError('Reopened experimental installation count changed')
        contacts = []
        for row in report['bearing_contacts']:
            gap, area = bearing_face(supports[row['support']], shape(row['mate'], True))
            if gap > 1e-6 or area < 1:
                raise ValueError('Lost reopened bearing face: ' + row['mate'])
            contacts.append(dict(support=row['support'], mate=row['mate'], gap_mm=gap, area_mm2=area))
        bolt_contacts = []
        for row in report['bolt_contacts']:
            gap, area = bearing_face(supports[row['support']], bolts[row['bolt']])
            if gap > 1e-6 or area < 1:
                raise ValueError('Lost reopened bolt head face: ' + row['bolt'])
            bolt_contacts.append(dict(bolt=row['bolt'], gap_mm=gap, area_mm2=area))
        dimensions = []
        for row in report['runs']:
            if row['mark'] not in {'M2175', 'M2176'}:
                continue
            expected = {'M2175': 822.325, 'M2176': 168.275}[row['mark']]
            actual = doc.getObject(row['id']).LinkedObject.Shape.optimalBoundingBox(False).XLength
            if abs(actual - expected) > 1e-6:
                raise ValueError('Printed inner support length changed: ' + row['id'])
            dimensions.append(dict(support=row['id'], actual_mm=actual, expected_mm=expected))
        # Exercise the face tests with actual saved shapes, not mirror assertions.
        native_support = supports['PortOuter_Run05']
        pin = shape('PortRollers_Unit012_PinAssembly_Pin', True)
        pin.translate(App.Vector(0, 0, -.2))
        pin_gap, pin_area = bearing_face(native_support, pin)
        bolt = bolts['PortOuter_Run05_Bolt00'].copy()
        bolt.translate(App.Vector(0, .2, 0))
        bolt_gap, bolt_area = bearing_face(native_support, bolt)
        if pin_gap <= 1e-6 and pin_area >= 1:
            raise ValueError('Contact test accepted a displaced pin')
        if bolt_gap <= 1e-6 and bolt_area >= 1:
            raise ValueError('Contact test accepted a displaced bolt head')
        result = dict(status='passed_experiment_checks_only', native_sha256=sha(native),
            support_solids=len(supports), bolt_solids=len(bolts), bearing_contacts=contacts,
            bolt_contacts=bolt_contacts, printed_dimensions=dimensions,
            negative_contacts=dict(displacement_mm=.2, pin_gap_mm=pin_gap, pin_area_mm2=pin_area,
                                   bolt_gap_mm=bolt_gap, bolt_area_mm2=bolt_area),
            historical_fit_qualified=False, promoted_to_delivery=False)
        write(out / 'reopened_checks.json', result)
        print('REOPENED CHECKS PASSED', len(contacts), 'pin/washer seats;', len(bolt_contacts), 'bolt seats', flush=True)
    finally:
        close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
