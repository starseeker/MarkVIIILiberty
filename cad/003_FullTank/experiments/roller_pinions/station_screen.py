"""Planar arithmetic screen of an unaccepted pinion station; no CAD fit claim."""
from pathlib import Path
import sys,json,math,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/markviii-pinion-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];REPO=STAGE.parents[1]
sys.path.insert(0,str(STAGE))
from lib.model import load,point,datum_values
from lib.evidence import fingerprint,sha
m=load();q={k:v.value for k,v in m['values'].items()}
x,z=point(m,'snl_2',[1614,422]);drive=datum_values('port_drive',m)['translation'];x-=drive[0];z-=drive[2]
D=math.hypot(x,z);groove_circle=q['drive_root_radius']+q['drive_groove_radius']
reported_radius=13.687*25.4/2;boss_radius=27.5;roller_circle=reported_radius-boss_radius
phi=math.atan2(-x,-z);count=9;phases=phi+np.arange(count)*2*math.pi/count
centers=np.column_stack([x+roller_circle*np.sin(phases),z+roller_circle*np.cos(phases)])
# Trace the existing unrounded circular tooth-relief construction. This planar
# screen excludes the adopted 3 mm crest fillets and all axial geometry.
theta=np.linspace(0,2*math.pi,12000);r=np.full_like(theta,q['drive_diameter']/2)
for n in range(int(q['drive_teeth'])):
 delta=(theta-n*2*math.pi/q['drive_teeth']+math.pi)%(2*math.pi)-math.pi
 projection=groove_circle*np.sin(delta)
 valid=(abs(projection)<=q['drive_groove_radius']) & (np.cos(delta)>0)
 candidate=groove_circle*np.cos(delta[valid])-np.sqrt(q['drive_groove_radius']**2-projection[valid]**2)
 r[valid]=np.minimum(r[valid],candidate)
fig,ax=plt.subplots(figsize=(11,7));ax.fill(r*np.sin(theta),r*np.cos(theta),color='#887854',alpha=.75,label='Current 35-tooth ring, crest fillets omitted')
ax.add_patch(Circle((0,0),q['drive_inner_diameter']/2,color='white'))
ax.add_patch(Circle((x,z),reported_radius,fill=False,ls=':',color='#597080',label='Printed diameter at bosses: interpretation open'))
ax.add_patch(Circle((x,z),roller_circle,fill=False,ls='--',color='#207d94',label='Illustrative roller-center circle'))
for n,(cx,cz) in enumerate(centers):
 ax.add_patch(Circle((cx,cz),25.4,color='#62b4c4',alpha=.8,label='2 inch roller envelopes' if n==0 else None))
 ax.plot(cx,cz,'+',color='#164b55')
ax.plot([0,x],[0,z],color='#bb4444',lw=1);ax.plot([0,x],[0,z],'x',color='#bb4444');ax.text(x+10,z+20,'SNL Plate 2 pick\n[1614, 422]',fontsize=9)
ax.text(-380,-120,'Drive axis unchanged\nNominal 35 teeth\n35/37 conflict remains',fontsize=10)
ax.set(xlabel='Forward from drive axis (mm)',ylabel='Above drive axis (mm)',aspect='equal',title='Preparatory pinion-station screen — not an accepted contact solution')
ax.set_xlim(-550,900);ax.set_ylim(-550,550);ax.grid(alpha=.18);ax.legend(loc='lower right',fontsize=8)
fig.text(.1,.015,'27.5 mm boss radius and roller phase are illustrative. No axial fit, continuous engagement or native clearance is established.',fontsize=8)
fig.tight_layout(rect=[0,.04,1,1]);out=ROOT/'station_screen';out.mkdir(exist_ok=True);fig.savefig(out/'station_screen.png',dpi=160);fig.savefig(out/'station_screen.svg');plt.close(fig)
record={'status':'unaccepted_planar_arithmetic_screen','pinion_source_pixel':[1614,422],'pick_uncertainty_pixels':3,'pinion_relative_axis_mm':[x,z],'fixed_axis_distance_mm':D,'drive_groove_center_radius_mm':groove_circle,'printed_diameter_at_bosses_mm':13.687*25.4,'illustrative_boss_radius_mm':boss_radius,'illustrative_roller_center_radius_mm':roller_circle,'center_distance_minus_reference_circles_mm':D-groove_circle-roller_circle,'alternative_if_printed_diameter_were_roller_center_circle_mm':D-groove_circle-reported_radius,'note':'Reference-circle arithmetic is not a material gap or engagement measure. The diagram omits axial geometry and crest fillets; phase merely aims one roller toward the drive axis. The casting boss radius and source pick are inferred and unaccepted. No authoring inputs changed.','source_path':m['calibrations']['snl_2']['image'],'authored_fingerprint':fingerprint(),'script_sha256':sha(__file__),'render_sha256':sha(out/'station_screen.png')}
record['source_sha256']=sha(REPO/record['source_path']);(out/'report.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['pinion_relative_axis_mm','fixed_axis_distance_mm','center_distance_minus_reference_circles_mm','alternative_if_printed_diameter_were_roller_center_circle_mm']},indent=2))
