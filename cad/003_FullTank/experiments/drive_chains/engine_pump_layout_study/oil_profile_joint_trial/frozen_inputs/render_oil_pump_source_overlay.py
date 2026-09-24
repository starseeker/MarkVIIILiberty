"""Project saved external pump BReps onto the conditional HB45 source view."""
import argparse,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
import FreeCAD as App
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(out/'runtime/matplotlib'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw

source=read(HERE/'engine_pump_layout_study/source_constraints.json')
path=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate45.png'
assert sha(path)==source['source_hashes'][str(path.relative_to(ROOT))]
im=Image.open(path).convert('RGB');sx=source['hb45_local_scales_mm_per_px']['horizontal'];sz=source['hb45_local_scales_mm_per_px']['vertical']
rows=[];keys=['lower_body','cover','cover_gasket','drain_plug','drain_gasket','body_plug']
fig,ax=plt.subplots(figsize=(10,8));ax.imshow(im)
for folder,color,label in [(HERE/'engine_oil_pump_mounting_study','#b23a24','Prior estimated shape/level'),
                           (base,'#0077aa','Revised source-proportioned trial')]:
    r=read(folder/'report.json');native=folder/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native))
    try:
        pose=json.loads(doc.EngineOilPump.ProposedEnginePlacementJSON)
        mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
        for row in r['occurrences']:
            if row['key'] not in keys:continue
            link=doc.getObject(row['name']);shape=link.LinkedObject.Shape.copy()
            shape.Placement=doc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement).multiply(shape.Placement)
            points,triangles=shape.tessellate(.1)
            # Accessory-end elevation. +Y projects left; crank datum and scales
            # come from the independently retained source-pick record.
            projected=[(640-v.y/sx,1057-(v.z+pose['z'])/sz) for v in points]
            for tri in triangles:draw.polygon([projected[i] for i in tri],fill=255)
        ax.contour(np.array(mask),levels=[127],colors=[color],linewidths=1.5)
        ax.plot([],[],color=color,label=label)
        rows.append(dict(native_sha256=sha(native),proposed_engine_z_mm=pose['z'],parts=keys))
    finally:App.closeDocument(doc.Name)
ax.set_xlim(420,850);ax.set_ylim(1600,1360)
ax.set_xlabel('Source pixel X');ax.set_ylabel('Source pixel Y')
ax.set_title('Actual CAD silhouettes / HB p68 Plate45\nConditional aviation reference; external pump parts only')
ax.legend(loc='lower right',framealpha=.95)
fig.tight_layout();image=out/'hb45_overlay.png';fig.savefig(image,dpi=150);plt.close(fig)
write(out/'source_overlay_receipt.json',dict(images={image.name:sha(image)},renderer_sha256=sha(Path(__file__)),
    source_sha256=sha(path),source_constraints_sha256=sha(HERE/'engine_pump_layout_study/source_constraints.json'),
    inputs=rows,projection=dict(center_x_px=640,crank_y_px=1057,horizontal_mm_per_px=sx,vertical_mm_per_px=sz,
        positive_Y_projects_left=True,tessellation_deflection_mm=.1),
    caveats=['Source local scales and connection-derived pose are conditional, so this is not an independent registration proof.',
             'Rasterized tessellation silhouettes have pixel error; quantitative envelope checks use native cylinders.',
             'External connection fittings, mounting hardware, upper strainer and shaft omitted to compare the visible lower casing.'],
    standard_assembly_modified=False,installation_qualified=False))
