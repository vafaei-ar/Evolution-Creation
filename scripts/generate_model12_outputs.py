"""Generate Model 12 chronology SVG."""
from pathlib import Path
from evolution_creation.domestication import EVIDENCE
OUT=Path("figures"); OUT.mkdir(exist_ok=True)
w,h=900,430; left,right=170,840; top=65
def x(age): return left+(right-left)*(1-age/14)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.axis{stroke:#333}</style>',
'<text x="450" y="30" text-anchor="middle" font-size="22">Domestication chronology: camel does not join the early-Neolithic cluster</text>',
f'<line class="axis" x1="{left}" y1="360" x2="{right}" y2="360"/>']
for age in [14,12,10,8,6,4,2,0]:
 xx=x(age); parts += [f'<line x1="{xx:.1f}" y1="354" x2="{xx:.1f}" y2="366" stroke="#555"/>',f'<text x="{xx:.1f}" y="385" text-anchor="middle" font-size="12">{age} ka</text>']
for i,item in enumerate(EVIDENCE):
 y=95+i*65; a=x(item.domestication_high_ka); b=x(item.domestication_low_ka)
 parts += [f'<text x="155" y="{y+5}" text-anchor="end" font-size="13">{item.name}</text>',f'<line x1="{a:.1f}" y1="{y}" x2="{b:.1f}" y2="{y}" stroke="#1f77b4" stroke-width="12"/>']
parts += [f'<line x1="{x(11):.1f}" y1="55" x2="{x(11):.1f}" y2="345" stroke="#d62728" stroke-dasharray="6 5"/>',
f'<text x="{x(11)+7:.1f}" y="55" font-size="12">11 ka proposed founder date</text>',
'<text x="450" y="415" text-anchor="middle" font-size="11">Bars are approximate domestication intervals. They are not biological lineage-origin dates.</text>','</svg>']
(OUT/"model12_domestication_timeline.svg").write_text("\n".join(parts))
