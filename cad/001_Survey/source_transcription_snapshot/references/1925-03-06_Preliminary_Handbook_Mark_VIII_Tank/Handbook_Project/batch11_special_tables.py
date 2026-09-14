"""Source braces, shared descriptions and indents for pages 207, 211 and 213."""
def customize(tables):
 for r in tables['207']['sections'][0]['rows']:
  if r['part'] in ['M-380','M-382']:r['description_brace']=True
 # OCR interleaved the five short pipe lengths with their shared right-hand block.
 t=tables['211'];rr=t['sections'][-1]['rows']
 starts=[2050,2075,2100,2125,2150,2187,2264,2290,2316]
 for r,start in zip(rr,starts):
  for j,line in enumerate(r['lines']):line['baseline']=start+25.2*j
  if r['part'] in ['SH981A','SH981B','SH981C','SH981D','SH981E','SH981G','SH981H']:
   r['short_width']=74 if r['part'] in ['SH981A','SH981B','SH981C','SH981D','SH981E'] else 69
   r['description_leader']=True
 t['shared_blocks']=[dict(x=211,width=135,baseline=2035,step=25.2,brace_x=208,brace_top=2022,brace_bottom=2167,lines=['Armored flexible brass tubing—½ inside diame-','ter Union and ½ male pipe adapter each end.','Armored flexible brass tubing ¼ inch inside','diam.—Union and ¼ male pipe adapter one end','and Union and ⅛-inch male pipe adapter other','end.']),dict(x=205,width=141,baseline=2264,step=25.2,brace_x=202,brace_top=2247,brace_bottom=2297,lines=['Armored flexible brass tubing—¼ inside diameter.','Union and ¼ male pipe adapters both ends.'])]
 # Nested component lines are indented as printed; a single brace covers C, D, E.
 t=tables['213'];rr=t['sections'][0]['rows']
 for r in rr:
  if r['part']=='SH982B':
   for j,line in enumerate(r['lines']):line['indent']=0 if j==0 else 10 if j==1 else 20
  elif r['part'] in ['SH982C','SH982D','SH982E']:
   r['short_width']=47
   for j,line in enumerate(r['lines']):line['indent']=10 if j else 0
   if r['part']=='SH982E':
    for line in r['lines'][1:]:line['width']=203
  elif r['part'] in ['982F','982G','982H']:
   for j,line in enumerate(r['lines']):line['indent']=0 if j==0 else 5 if line['text'] in ['to each tube:','parts:'] else 10
 t['shared_blocks']=[dict(x=183,width=163,baseline=rr[1]['lines'][0]['baseline'],step=25.2,brace_x=180,brace_top=613,brace_bottom=688,lines=['Copper tubing.','¼ outside diameter.','Fastened to each tube are:'])]
