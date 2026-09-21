"""Generate Model 13 SVG output."""
from pathlib import Path
from evolution_creation.inserted_pair_detectability import at_least_one_marker_detected
OUT=Path("figures"); OUT.mkdir(exist_ok=True)
p=.01
ks=[1,10,100,500,1000]
vals=[at_least_one_marker_detected(p,k) for k in ks]
w,h=900,430; left,top,pw,ph=90,60,760,300
px=lambda i:left+pw*i/(len(ks)-1); py=lambda v:top+ph*(1-v)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}</style>',
'<text x="450" y="30" text-anchor="middle" font-size="22">Many distinctive private markers make complete genetic invisibility harder</text>']
for k in range(6):
 v=k/5; y=py(v); parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>']
for i,(k,v) in enumerate(zip(ks,vals)):
 x=px(i); parts += [f'<circle cx="{x:.1f}" cy="{py(v):.1f}" r="7" fill="#1f77b4"/>',f'<text x="{x:.1f}" y="385" text-anchor="middle" font-size="12">{k}</text>']
parts += [f'<polyline fill="none" stroke="#1f77b4" stroke-width="3" points="{" ".join(f"{px(i):.1f},{py(v):.1f}" for i,v in enumerate(vals))}"/>',
'<text x="450" y="414" text-anchor="middle" font-size="11">Independent-marker approximation with 1% per-marker survival+sampling probability.</text>','</svg>']
(OUT/"model13_marker_detectability.svg").write_text("\n".join(parts))
