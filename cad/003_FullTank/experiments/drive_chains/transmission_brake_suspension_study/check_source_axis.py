"""Check the manually picked HB134 shaft center against its scanned opening.

A blurred threshold and robust axis-aligned ellipse fit are a local pixel check,
not dimensional calibration. The unoccluded hole boundary is used; no claim that
this recovers scan distortion, pin position, or an original production dimension.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
from scipy.ndimage import label, binary_erosion
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[5]
source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate134.png'
a=np.array(Image.open(source).convert('L').filter(ImageFilter.GaussianBlur(3)))
mask=a[380:820,580:1020]>200
labels,_=label(mask);region=labels==labels[593-380,792-580]
assert labels[593-380,792-580]!=0
boundary=region&~binary_erosion(region);yy,xx=np.nonzero(boundary);x=xx+580;y=yy+380
fit=least_squares(lambda v:((x-v[0])/v[2])**2+((y-v[1])/v[3])**2-1,[792,593,140,145],loss='soft_l1')
result=dict(source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    manual_center_px=[792,593],fitted_center_px=fit.x[:2].tolist(),fitted_semiaxes_px=fit.x[2:].tolist(),
    center_difference_px=(fit.x[:2]-[792,593]).tolist(),normalized_residual_rms=float(np.sqrt(np.mean(fit.fun**2))),
    blur_radius_px=3,threshold=200,crop_xyxy=[580,380,1020,820],
    interpretation='Fit agrees with the manual shaft-center pick within its 4 px allowance. It does not remove the model/source channel registration discrepancy.',
    within_manual_pick_allowance=bool(np.max(np.abs(fit.x[:2]-[792,593]))<4))
assert result['within_manual_pick_allowance']
Path(__file__).with_name('source_axis_check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
