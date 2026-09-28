"""Freeze catalogue context, original fitting views and proposed support interfaces."""
import hashlib,importlib,json,re,sys
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[3];N=H/'driver_foot_reverse_study';out=N/'reverse_fittings_sources01';out.mkdir(exist_ok=False)
SNL=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project';HB=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();deps={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
terms=['M779','M781','M780','M778','M739','M740','M742','M744','M745'];rows=[];pages={}
sys.path.insert(0,str(SNL))
for f in sorted((SNL/'data').glob('*.py')):
    module=importlib.import_module('data.'+f.stem)
    if not hasattr(module,'TABLES'):continue
    deps[str(f.relative_to(ROOT))]=sha(f)
    for page,rs in module.TABLES.items():
        for i,r in enumerate(rs,1):
            matched=[v for v in terms if re.search(r'(?<![A-Za-z0-9])'+v+r'(?![A-Za-z0-9])',json.dumps(r))]
            if matched:
                rows.append(dict(source_id=f'SNL:{page:03d}:{i:03d}',matched_terms=matched,**r));pages[page]=[dict(source_id=f'SNL:{page:03d}:{j:03d}',**v) for j,v in enumerate(rs,1)]
images=[]
for page in sorted(pages):
    source=SNL/'sources'/f'p{page:03d}.jpg';deps[str(source.relative_to(ROOT))]=sha(source)
    im=Image.open(source).rotate(-90,expand=True);im.thumbnail((2100,2100));target=out/f'snl{page:03d}.png';im.save(target);images.append(dict(file=target.name,sha256=sha(target),source=str(source.relative_to(ROOT)),rotation_degrees=-90))
for f in ['plate06.png','plate94.png','plate113.png']:
    source=HB/'assets'/f;deps[str(source.relative_to(ROOT))]=sha(source);im=Image.open(source);im.thumbnail((2100,2100));target=out/('hb_'+f);im.save(target);images.append(dict(file=target.name,sha256=sha(target),source=str(source.relative_to(ROOT))))
index=ROOT/'cad/001_Survey/inputs/figure_index.json';deps[str(index.relative_to(ROOT))]=sha(index)
figures=[r for r in json.loads(index.read_text()) if any(w in str(r).lower() for w in ['control system','control rods','driver’s seat','positions of reversing'])]
(out/'report.json').write_text(json.dumps(dict(selected_rows=rows,complete_selected_pages=pages,images=images,reviewed_figure_index_matches=figures,input_hashes=deps,source_camera_refitted=False,geometry_created=False),indent=2)+'\n')
print(len(rows),'selected rows;',len(images),'source views',flush=True)
