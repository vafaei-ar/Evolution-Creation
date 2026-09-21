"""Generate Model 11 SVG output."""
from pathlib import Path
import numpy as np
from evolution_creation.admixture_genealogy import pulse_genealogical_fraction

OUT=Path("figures"); OUT.mkdir(exist_ok=True)
gs=np.arange(1,13)
vals=[pulse_genealogical_fraction(.01,int(g)) for g in gs]
w,h=900,470; left,top,pw,ph=80,60,760,320
px=lambda g:left+pw*(g-1)/(gs[-1]-1)
py=lambda v:top+ph*(1-v)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<rect width="100%" height="100%" fill="white"/>',
'<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke:#1f77b4;stroke-width:3}</style>',
'<text x="450" y="30" text-anchor="middle" font-size="22">1% genetic pulse can spread genealogically without becoming 100% DNA ancestry</text>']
for k in range(6):
 v=k/5; y=py(v); parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>']
pts=" ".join(f"{px(int(g)):.1f},{py(float(v)):.1f}" for g,v in zip(gs,vals))
parts += [f'<polyline class="line" points="{pts}"/>',
f'<line x1="{left}" y1="{py(.01):.1f}" x2="{left+pw}" y2="{py(.01):.1f}" stroke="#ff7f0e" stroke-width="3" stroke-dasharray="7 5"/>',
'<text x="610" y="105" font-size="12">genealogical descendant fraction</text>',
'<text x="610" y="126" font-size="12">orange dashed: expected 1% source-DNA mean</text>',
'<text x="450" y="425" text-anchor="middle" font-size="15">Generations since a single 1% source-admixture pulse</text>',
'<text x="20" y="225" transform="rotate(-90 20 225)" text-anchor="middle" font-size="15">Population fraction</text>',
'<text x="450" y="455" text-anchor="middle" font-size="11">Neutral random-mating illustration; genealogical and genetic ancestry are different state variables.</text>','</svg>']
(OUT/"model11_admixture_vs_genealogy.svg").write_text("\n".join(parts))
