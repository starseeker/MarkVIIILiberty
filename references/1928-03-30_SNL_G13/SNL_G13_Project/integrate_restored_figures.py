#!/usr/bin/env python3
"""Change only image links in the delivered SLA, retaining all object geometry."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent

def main():
    manifest=json.loads((ROOT/'restoration/manifest.json').read_text())
    for filename in ['SNL_G13_Pilot.sla','Foldout_Plate_2.sla']:
        path=ROOT/filename;text=path.read_text();changes=0
        for n in manifest:
            old=f'PFILE="assets/p{n}-geometry.png"';new=f'PFILE="restoration/clean/p{n}-clean.png"'
            if old in text:
                assert text.count(old)==1,(filename,n)
                text=text.replace(old,new);changes+=1
        path.write_text(text)
        links=[x.get('PFILE') for x in ET.fromstring(text).findall('.//PAGEOBJECT') if x.get('PFILE','').startswith('restoration/clean/')]
        assert len(links)==(31 if filename.startswith('SNL') else 1)
        assert all((ROOT/p).is_file() for p in links)
        print(filename,changes,'image links updated; native XML otherwise unchanged.')

if __name__=='__main__':main()
