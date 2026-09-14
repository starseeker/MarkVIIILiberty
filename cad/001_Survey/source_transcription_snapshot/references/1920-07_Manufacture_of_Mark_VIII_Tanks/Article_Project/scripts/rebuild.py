"""Portable unattended rebuild with an isolated OpenType font set (Scribus 1.6.x)."""
from pathlib import Path
from xml.sax.saxutils import escape
import os,shutil,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
binary=shutil.which('scribus') or shutil.which('scribus-ng')
if not binary:raise SystemExit('Install Scribus 1.6.x, or execute build_project.py from Scribus.')
with tempfile.TemporaryDirectory(prefix='jordan-scribus-') as td:
 p=Path(td);config=p/'fonts.conf'
 config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>'+escape(str(ROOT/'fonts'))+'</dir><dir>/usr/share/fonts/truetype/dejavu</dir><cachedir>'+escape(str(p/'fontcache'))+'</cachedir></fontconfig>')
 env=os.environ.copy();env.update(FONTCONFIG_FILE=str(config),JORDAN_BATCH='1')
 (p/'prefs').mkdir()
 subprocess.run([binary,'-platform','offscreen','-pr',str(p/'prefs'),'-g','-ns','-py',str(ROOT/'build_project.py')],env=env,check=True)
 if (ROOT/'build_error.txt').exists():raise SystemExit((ROOT/'build_error.txt').read_text())
 if not (ROOT/'data/build_success.json').exists():raise SystemExit('Scribus did not complete; inspect its diagnostics.')
 subprocess.run([sys.executable,str(ROOT/'scripts/check_and_compare.py')],check=True)
