"""Correct the Plate 133 crop to retain its complete upper edge."""
from pathlib import Path
import scribus as s,json,os,traceback
R=Path(__file__).resolve().parent
try:
 a=next(x for x in json.loads((R/'data/assets.json').read_text()) if x['name']=='plate133')
 s.openDoc(str(R/'Handbook_Master.sla'));s.gotoPage(226);name='p226-plate133'
 s.moveObjectAbs(198+(a['crop'][0]-a['content_center_px'])*.225,17+a['crop'][1]*.225,name)
 s.sizeObject(a['output_size'][0]*.225,a['output_size'][1]*.225,name)
 s.loadImage(str(R/'assets/plate133.png'),name);s.setScaleImageToFrame(True,True,name)
 s.gotoPage(1);s.saveDocAs(str(R/'Handbook_Master.sla'))
except Exception:
 (R/'plate-update-error.txt').write_text(traceback.format_exc())
finally:
 if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
