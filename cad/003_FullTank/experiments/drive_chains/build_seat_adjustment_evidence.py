"""Retain seat-family references without inventing adjustment topology or counts."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
from PIL import Image

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
SNL = ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project'
HB = ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank'
sys.path.insert(0, str(SNL))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    out = p.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'report.json').exists()
    deps = {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))}

    def bind(path):
        deps[str(path.relative_to(ROOT))] = sha(path)

    rows, all_rows = [], []
    for file in sorted((SNL/'data').glob('*.py')):
        module = importlib.import_module('data.'+file.stem)
        if not hasattr(module, 'TABLES'):
            continue
        bind(file)
        for page, values in module.TABLES.items():
            for index, row in enumerate(values, 1):
                item = dict(source_id=f'SNL:{page:03d}:{index:03d}', **row)
                all_rows.append(item)
                text = json.dumps(row, ensure_ascii=False)
                if any(term in text for term in ['SH291', 'M791', 'driver’s seat']):
                    rows.append(item)
    images = []
    for page in [64, 65, 66, 102, 103, 104, 166, 191, 207]:
        source = SNL/'sources'/f'p{page:03d}.jpg'
        bind(source)
        im = Image.open(source).rotate(-90, expand=True)
        rotated = list(im.size)
        im.thumbnail((2000, 2000))
        file = out/f'p{page:03d}_overview.png'
        im.save(file)
        images.append(dict(file=file.name, source=str(source.relative_to(ROOT)),
                           source_sha256=sha(source), rotation_degrees=-90,
                           rotated_size=rotated, output_size=list(im.size), sha256=sha(file)))
    for source, file, box in [
            (HB/'Handbook_Project/assets/plate06.png','hb_plate06_overview.png',None),
            (HB/'original_scans/MarkVIII009.jpg','hb6_seat_original.png',(560,500,1080,1175))]:
        bind(source)
        im = Image.open(source)
        if box:
            im = im.crop(box)
        else:
            im.thumbnail((1900,1700))
        im.save(out/file)
        images.append(dict(file=file, source=str(source.relative_to(ROOT)),
                           source_sha256=sha(source), crop_original_pixels=box,
                           output_size=list(im.size),sha256=sha(out/file)))
    bind(HB/'Handbook_Project/prepare_assets.py')
    result = dict(evidence_only=True, geometry_created=False, source_camera_refitted=False,
        input_hashes=deps, searched_rows=len(all_rows), selected_rows=rows, images=images,
        inventory_candidates=[
            dict(mark='SH291C',source='SNL:066:006',quantity=1,printed_length_mm=88.9,
                 disposition='Separate source identity from the two SH291X clips. Mount, length datum and relation to the adjustable-seat assembly unresolved.'),
            dict(mark='SH291D',source='SNL:166:010',kind='handle',quantity=None,
                 printed_rivet_diameter_mm=6.35,printed_rivet_length_mm=12.7,rivets_per_named_application=2,
                 disposition='Functional rivet application confirmed in original. Seat-family association inferred from SH291 prefix/drawing291, not an explicit mounting instruction or quantity.'),
            dict(mark='SH291F',source='SNL:191:003',kind='cleat',quantity=None,
                 printed_rivet_diameter_mm=4.7625,printed_rivet_length_mm=25.4,rivets_per_named_application=10,
                 disposition='Functional rivet application confirmed in original. Installed count, mounting surface and seat-adjustment role unresolved.')],
        original_scan_observations=[
            'SNL166 explicitly names handle SH291D with two quarter-inch by half-inch button-head rivets. The generic26 total spans other applications and is not a seat count.',
            'SNL191 explicitly names cleat SH291F with ten3/16-inch by1-inch countersunk rivets. The generic56 total spans other applications and is not a seat count.',
            'SNL207 retains one M791 (drawing291), fourSH289E bearings and twoSH291X clips. It does not include the D/F names in that composed-of list.',
            'SNL103–104 HANDLE entries and SNL65 CLEAT entries contain no standalone SH291D/F respectively. The generic fastener references remain evidence of otherwise unlisted items, not proof that their geometry or seat location is known.',
            'HB6 and its original halftone crop show the curved back, under-seat framework and central vertical member among the controls. No visible member can be confidently assigned to SH291C/D/F from this view alone.',
            'No camera fit: the visible features lack independent identified3D anchors. Photographic foreshortening must not supply unqualified dimensions.'],
        next_action='Keep all three identities unresolved in the inventory. Continue the supported side-plate fore-edge correction, then the identifiable foot/reverse controls. Do not add speculative clips, handles, cleats or twelve rivets solely to fill inventory counts.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Seat adjustment references saved;',len(rows),'selected rows; geometry and installed counts unchanged.')


if __name__ == '__main__':
    main()
