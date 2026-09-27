"""Reproducible original-source details for the unresolved foot-control connections."""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
HB=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[];deps={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
def save(name,source,im,operations):
    file=out/name;im.save(file);deps[str(source.relative_to(ROOT))]=sha(source)
    records.append(dict(file=name,sha256=sha(file),source=str(source.relative_to(ROOT)),operations=operations))
source=HB/'Handbook_Project/assets/plate92.png';im=Image.open(source)
save('hb92_unlabelled_driver_detail.png',source,im.crop((0,0,510,560)).transpose(Image.Transpose.ROTATE_90).resize((1400,1275)),
     ['crop0,0,510,560','rotate90CCW','resize1400x1275'])
source=HB/'Handbook_Project/assets/plate113.png';im=Image.open(source)
save('hb113_driver_side_detail.png',source,im.crop((0,0,590,650)).transpose(Image.Transpose.ROTATE_90).resize((1300,1180)),
     ['crop0,0,590,650','rotate90CCW','resize1300x1180'])
source=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p280-geometry.png';im=Image.open(source)
save('snl6_driver_plan_detail.png',source,im.crop((0,100,590,490)).resize((1770,1170)),['crop0,100,590,490','resize1770x1170'])
source=HB/'Handbook_Project/assets/plate12.png';save('hb12_lubrication_view.png',source,Image.open(source),['original'])
sys.path.insert(0,str(HB/'Handbook_Project'));from prepare_assets import page
prep=HB/'Handbook_Project/prepare_assets.py';deps[str(prep.relative_to(ROOT))]=sha(prep)
source=HB/'original_scans/MarkVIII075.jpg';im=page(149,HB/'original_scans');im.thumbnail((1700,2200))
save('hb149_original.png',source,im,['prepare_assets.page149','thumbnail1700x2200'])
index=ROOT/'cad/001_Survey/inputs/figure_index.json';deps[str(index.relative_to(ROOT))]=sha(index)
figures=[r for r in json.loads(index.read_text()) if any(t in r.get('caption','').lower() for t in ['control','brake','lubricat'])]
(out/'report.json').write_text(json.dumps(dict(input_hashes=deps,images=records,relevant_figure_index=figures,
    source_camera_refitted=False,geometry_created=False,scope='Original source crops and enclosing pedal description; no new geometry or interpretation certified.'),indent=2)+'\n')
print('Saved',len(records),'original views and',len(figures),'figure-index entries.',flush=True)
