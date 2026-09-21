"""Generate Model 14 Bayesian sensitivity SVG."""
from pathlib import Path
import numpy as np
from evolution_creation.agency_bayes import posterior_from_prior_lr
OUT=Path("figures"); OUT.mkdir(exist_ok=True)
lrs=np.logspace(-2,5,220); priors=[.001,.01,.1,.5]; colors=["#1f77b4","#ff7f0e","#2ca02c","#d62728"]
w,h=900,470; left,top,pw,ph=90,60,750,320
px=lambda lr:left+pw*(np.log10(lr)+2)/7
py=lambda v:top+ph*(1-v)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
'<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
'<text x="450" y="30" text-anchor="middle" font-size="22">The same likelihood ratio gives different posteriors under different priors</text>']
for k in range(6):
 v=k/5; y=py(v);parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>']
for i,p in enumerate(priors):
 pts=" ".join(f"{px(x):.1f},{py(posterior_from_prior_lr(p,float(x))):.1f}" for x in lrs)
 parts += [f'<polyline class="line" stroke="{colors[i]}" points="{pts}"/>',f'<text x="650" y="{88+i*21}" font-size="12" fill="{colors[i]}">prior {p:g}</text>']
parts += ['<text x="450" y="425" text-anchor="middle" font-size="15">Likelihood ratio / Bayes factor (log scale)</text>','<text x="20" y="225" transform="rotate(-90 20 225)" text-anchor="middle" font-size="15">Posterior probability</text>','<text x="450" y="455" text-anchor="middle" font-size="11">Bayesian structure alone does not provide empirical values for cosmic priors or likelihoods.</text>','</svg>']
(OUT/"model14_bayesian_sensitivity.svg").write_text("\n".join(parts))
