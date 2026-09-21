"""Generate Model 15 output."""
from pathlib import Path
from evolution_creation.moral_evolution import simulate_norm_dynamics, simulate_conformity_only
OUT=Path("figures"); OUT.mkdir(exist_ok=True)
cases=[
 ("costly cooperation, no punishment",simulate_norm_dynamics(.6,400,.05,.2,0,0).cooperative_fraction),
 ("punishment supports cooperation",simulate_norm_dynamics(.6,400,.05,.2,.8,0).cooperative_fraction),
 ("conformity: initial majority",simulate_conformity_only(.8,400,.05,1.0)),
 ("conformity: initial minority",simulate_conformity_only(.2,400,.05,1.0)),
]
colors=["#d62728","#2ca02c","#1f77b4","#ff7f0e"]
w,h=900,470; left,top,pw,ph=90,60,750,320
px=lambda i,n:left+pw*i/(n-1); py=lambda v:top+ph*(1-v)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
'<text x="450" y="30" text-anchor="middle" font-size="22">Punishment can stabilize cooperation; conformity stabilizes whichever norm is common</text>']
for k in range(6):
 v=k/5; y=py(v); parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>']
for i,(label,vals) in enumerate(cases):
 pts=" ".join(f"{px(j,len(vals)):.1f},{py(float(v)):.1f}" for j,v in enumerate(vals))
 parts += [f'<polyline class="line" stroke="{colors[i]}" points="{pts}"/>',f'<text x="545" y="{86+i*21}" font-size="12" fill="{colors[i]}">{label}</text>']
parts += ['<text x="450" y="425" text-anchor="middle" font-size="15">Model time</text>','<text x="20" y="225" transform="rotate(-90 20 225)" text-anchor="middle" font-size="15">Behavior frequency</text>','<text x="450" y="455" text-anchor="middle" font-size="11">Conformity is content-neutral: a majority norm can be prosocial or harmful.</text>','</svg>']
(OUT/"model15_norm_dynamics.svg").write_text("\n".join(parts))
