"""A vector overlay on unchanged source pixels; no raster refitting or editing."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.model import load,point
data=load();origin=point(data,'snl_2',[0,0]);unit=point(data,'snl_2',[1,1])
report=json.loads((ROOT/'installed_pitch_route_report.json').read_text())
def pixel(coords):return [(coords[i]-origin[i])/(unit[i]-origin[i]) for i in range(2)]
new=pixel(report['candidate_transmission_axis_xz_mm']);old=pixel(report['provisional_transmission_axis_xz_mm'])
big=pixel(report['roller_pinion_axis_xz_mm'])
points=[pixel(p) for p in report['vertices_world_xz_mm']]
poly=' '.join(f'{x:.6f},{z:.6f}' for x,z in points+[points[0]])
source='../../../../'+data['calibrations']['snl_2']['image']
from PIL import Image
width,height=Image.open(STAGE.parents[1]/data['calibrations']['snl_2']['image']).size
page=f'''<!doctype html><meta charset="utf-8"><title>Drive-chain route versus SNL Plate2</title>
<style>body{{font:16px system-ui;background:#f7f5ed;color:#26332b;max-width:1300px;margin:2em auto;padding:0 1em}}svg{{width:100%;background:white;border:1px solid #a9b2a8}}label{{display:inline-block;margin:0 1em 1em 0}}p{{max-width:90ch}}.point{{fill:none;stroke-width:1.2}}text{{font:5px system-ui;paint-order:stroke;stroke:#fff;stroke-width:1.5px;stroke-linejoin:round}}</style>
<h1>Drive-chain route versus SNL Plate2</h1>
<p>The 50-pitch calculation retains the roller pinion's 17.21° phase and derives
a transmission-sprocket station. It is a mathematical candidate; native parts,
physical clearances and the catalogue quantity conflict remain unresolved.</p>
<label><input type="checkbox" data-layer="old" checked>Old provisional layout</label>
<label><input type="checkbox" data-layer="candidate" checked>Chain-derived candidate</label>
<label><input type="checkbox" data-layer="route" checked>50-pitch route</label>
<label>Source opacity <input id="opacity" type="range" min="0.2" max="1" step="0.05" value="0.85"></label>
<svg viewBox="1320 350 380 185" role="img" aria-label="Unchanged SNL section with the two transmission-axis candidates and a closed chain pitch polygon">
<image id="source" href="{source}" x="0" y="0" width="{width}" height="{height}" opacity="0.85"/>
<g id="route" stroke="#087780" fill="none"><polyline points="{poly}" stroke-width="0.65"/>
{''.join(f'<circle cx="{x:.6f}" cy="{z:.6f}" r="0.8" stroke-width="0.45"/>' for x,z in points)}</g>
<g id="old" stroke="#c53a35"><circle class="point" cx="{old[0]}" cy="{old[1]}" r="3"/><path d="M {old[0]-5},{old[1]} h 10 M {old[0]},{old[1]-5} v 10" stroke-width="0.5"/><text x="{old[0]-50}" y="{old[1]+15}" fill="#a31c1c">Old layout (1390,455)</text></g>
<g id="candidate" stroke="#234cdf"><circle class="point" cx="{new[0]}" cy="{new[1]}" r="3"/><path d="M {new[0]-5},{new[1]} h 10 M {new[0]},{new[1]-5} v 10" stroke-width="0.5"/><circle class="point" cx="{big[0]}" cy="{big[1]}" r="3"/><text x="{new[0]+5}" y="{new[1]+14}" fill="#173aaa">Candidate ({new[0]:.2f},{new[1]:.2f})</text></g>
</svg>
<p>The source calibration and pixels are unchanged. The derived station is
{report['provisional_station_difference_mm']:.2f} mm from the old provisional
layout datum. Its projection lies near the visible shaft center in this section.
That visual comparison was made after calculating the candidate; it is not an
independent metric acceptance or proof of historical fit.</p>
<p>Center distance: {report['center_distance_mm']:.3f} mm. Pitch: 76.2 mm.
The 12 big-circle and six small-circle vertices align with the selected 23/12
tooth phases. Tooth-center alignment alone does not qualify tooth profiles,
bar clearance or running engagement. The transmission datum has not been edited.</p>
<p><a href="installed_pitch_route_report.json">Calculation record</a> · <a href="../../packets/R02-drive-chains.md">Source conflicts and next geometry work</a></p>
<script>for(const input of document.querySelectorAll('[data-layer]'))input.addEventListener('change',()=>document.getElementById(input.dataset.layer).style.display=input.checked?'':'none');document.getElementById('opacity').addEventListener('input',event=>document.getElementById('source').style.opacity=event.target.value);</script>
'''
(ROOT/'route_comparison.html').write_text(page)
print('Created',ROOT/'route_comparison.html')
