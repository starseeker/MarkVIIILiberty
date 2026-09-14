"""Embedded fonts for consistent comparison-report rendering."""
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
F=Path(__file__).resolve().parent/'fonts/proof-fonts'
pdfmetrics.registerFont(TTFont('ProofSans',str(F/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('ProofSans-Bold',str(F/'DejaVuSans-Bold.ttf')))
