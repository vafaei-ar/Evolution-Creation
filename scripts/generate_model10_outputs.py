"""Generate deterministic SVG assets for Model 10."""

from pathlib import Path

import numpy as np

from evolution_creation.evidence_calibration import (
    BYARD_POPULATION_MODEL_SET,
    preclosure_generations,
    required_external_parent_rate,
    sample_evidence_envelope,
    simulate_bottleneck_fixation_probability,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


def _svg(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="22">{title}</text>',
    ]


def required_rate_svg():
    ns = BYARD_POPULATION_MODEL_SET.astype(float)
    left, top, w, h = 90, 65, 780, 370
    ymin, ymax = 0.0, 0.027
    px = lambda n: left + w * (n - ns.min()) / (ns.max() - ns.min())
    py = lambda v: top + h * (1 - (v - ymin) / (ymax - ymin))
    parts = _svg(940, 540, "Required external-parent rate under published population models")
    for pct in [0, .5, 1, 1.5, 2, 2.5]:
        y = py(pct / 100)
        parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+w}" y2="{y:.1f}"/>',
                  f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{pct:g}%</text>']
    for g, dash in [(8, ""), (9, ' stroke-dasharray="8 5"')]:
        for target, color in [(.5, COLORS[0]), (.95, COLORS[1])]:
            vals = [required_external_parent_rate(target, g, int(n)) for n in ns]
            pts = " ".join(f"{px(n):.1f},{py(v):.1f}" for n, v in zip(ns, vals))
            parts.append(f'<polyline class="line" stroke="{color}"{dash} points="{pts}"/>')
    labels = [(COLORS[0],"","50%, 8 gen"),(COLORS[1],"","95%, 8 gen"),
              (COLORS[0],' stroke-dasharray="8 5"',"50%, 9 gen"),
              (COLORS[1],' stroke-dasharray="8 5"',"95%, 9 gen")]
    for i,(color,dash,label) in enumerate(labels):
        y=82+i*22
        parts += [f'<line x1="610" y1="{y}" x2="645" y2="{y}" stroke="{color}" stroke-width="3"{dash}/>',
                  f'<text x="655" y="{y+5}" font-size="12">{label}</text>']
    for n in [3848,6789,8144,10093,12106]:
        parts.append(f'<text x="{px(n):.1f}" y="459" text-anchor="middle" font-size="12">{n:,}</text>')
    parts += ['<text x="480" y="488" text-anchor="middle" font-size="15">Contact-era population size</text>',
              '<text x="22" y="250" transform="rotate(-90 22 250)" text-anchor="middle" font-size="15">Required external-parent probability per parental draw</text>',
              '<text x="470" y="516" text-anchor="middle" font-size="11">Independence approximation; Monte Carlo validation is in the notebook.</text>',
              '</svg>']
    (OUT/"model10_required_rate_envelope.svg").write_text("\n".join(parts))


def isolation_svg():
    ages=np.arange(9000,13501,100)
    low=np.array([preclosure_generations(11000,a,30) for a in ages])
    high=np.array([preclosure_generations(11000,a,26) for a in ages])
    left,top,w,h=90,65,780,330
    ymax=max(int(high.max()),1)
    px=lambda a:left+w*(a-9000)/(13500-9000)
    py=lambda v:top+h*(1-v/ymax)
    parts=_svg(940,500,"Pre-closure generations versus Tasmania isolation date")
    for v in [0,20,40,60,80]:
        if v<=ymax:
            y=py(v); parts += [f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+w}" y2="{y:.1f}"/>',
                               f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v}</text>']
    upper=" ".join(f"{px(a):.1f},{py(v):.1f}" for a,v in zip(ages,high))
    lower=" ".join(f"{px(a):.1f},{py(v):.1f}" for a,v in zip(ages[::-1],low[::-1]))
    parts.append(f'<polygon points="{upper} {lower}" fill="{COLORS[0]}" opacity=".18"/>')
    xf=px(11000); l=px(11960); r=px(12890)
    parts += [f'<line x1="{xf:.1f}" y1="{top}" x2="{xf:.1f}" y2="{top+h}" stroke="{COLORS[3]}" stroke-dasharray="6 5"/>',
              f'<rect x="{l:.1f}" y="{top}" width="{r-l:.1f}" height="{h}" fill="{COLORS[2]}" opacity=".13"/>',
              '<text x="480" y="447" text-anchor="middle" font-size="15">Isolation age (years BP)</text>',
              '<text x="22" y="235" transform="rotate(-90 22 235)" text-anchor="middle" font-size="15">Generations available before closure</text>',
              '<text x="470" y="476" text-anchor="middle" font-size="11">Green band: 11.96-12.89 ka direct sea-level bracket; founder date: 11 ka.</text>',
              '</svg>']
    (OUT/"model10_isolation_window.svg").write_text("\n".join(parts))


def envelope_svg():
    env=sample_evidence_envelope(samples=50000,seed=20260920)
    r50=100*env.required_rate_50; r95=100*env.required_rate_95
    q50=np.quantile(r50,[.05,.5,.95]); q95=np.quantile(r95,[.05,.5,.95])
    left,top,w,h=100,70,740,280
    xmin,xmax=.6,2.7
    px=lambda x:left+w*(x-xmin)/(xmax-xmin)
    parts=_svg(940,500,"Evidence-envelope required mixing thresholds")
    bins=np.linspace(xmin,xmax,36)
    for values,color,y0,label in [(r50,COLORS[0],175,"50% fixation"),(r95,COLORS[1],315,"95% fixation")]:
        hist,_=np.histogram(values,bins=bins); scale=80/max(hist.max(),1)
        for i,v in enumerate(hist):
            x0=px(bins[i]); x1=px(bins[i+1]); hh=v*scale
            parts.append(f'<rect x="{x0:.1f}" y="{y0-hh:.1f}" width="{x1-x0-1:.1f}" height="{hh:.1f}" fill="{color}" opacity=".75"/>')
        parts.append(f'<text x="{left}" y="{y0-95}" font-size="13" font-weight="bold">{label}</text>')
    parts += [f'<text x="{left}" y="402" font-size="12">50%: 5th/median/95th = {q50[0]:.2f}% / {q50[1]:.2f}% / {q50[2]:.2f}%</text>',
              f'<text x="{left}" y="423" font-size="12">95%: 5th/median/95th = {q95[0]:.2f}% / {q95[1]:.2f}% / {q95[2]:.2f}%</text>',
              '<text x="470" y="475" text-anchor="middle" font-size="11">Uniform interval sampling and equal population-model weights are propagation conventions, not posteriors.</text>',
              '</svg>']
    (OUT/"model10_uncertainty_envelope.svg").write_text("\n".join(parts))


def bottleneck_svg():
    rates=np.linspace(.005,.035,13)
    constant=[]; bottleneck=[]
    for i,r in enumerate(rates):
        constant.append(simulate_bottleneck_fixation_probability(r,[7465]*9,5000,100+i))
        bottleneck.append(simulate_bottleneck_fixation_probability(r,[7465,342,342,342,342,342,342,342,342],5000,200+i))
    left,top,w,h=90,65,780,350
    px=lambda x:left+w*(x-.005)/.03
    py=lambda v:top+h*(1-v)
    parts=_svg(940,520,"Demographic-collapse sensitivity")
    for vals,color in [(constant,COLORS[0]),(bottleneck,COLORS[1])]:
        pts=" ".join(f"{px(r):.1f},{py(v):.1f}" for r,v in zip(rates,vals))
        parts.append(f'<polyline class="line" stroke="{color}" points="{pts}"/>')
    parts += [f'<line x1="590" y1="85" x2="625" y2="85" stroke="{COLORS[0]}" stroke-width="3"/><text x="635" y="90" font-size="12">constant N=7,465</text>',
              f'<line x1="590" y1="109" x2="625" y2="109" stroke="{COLORS[1]}" stroke-width="3"/><text x="635" y="114" font-size="12">then N=342</text>',
              '<text x="480" y="465" text-anchor="middle" font-size="15">External-parent probability per parental draw</text>',
              '<text x="470" y="495" text-anchor="middle" font-size="11">Sensitivity only. The bottleneck is not a historical reconstruction of ancestry-neutral survival.</text>',
              '</svg>']
    (OUT/"model10_bottleneck_sensitivity.svg").write_text("\n".join(parts))


def animation_svg():
    n=7465; frames=[]
    for g in [8,9]:
        frames.append((g,100*required_external_parent_rate(.5,g,n),100*required_external_parent_rate(.95,g,n)))
    parts=_svg(900,360,"One extra generation roughly halves the required threshold")
    for y,label in [(125,"50% fixation"),(225,"95% fixation")]:
        parts += [f'<rect x="220" y="{y-18}" width="570" height="32" rx="5" fill="#eee"/>',
                  f'<text x="202" y="{y+4}" text-anchor="end" font-size="13">{label}</text>']
    for i,(g,r50,r95) in enumerate(frames):
        vals=["0","0"]; vals[i]="1"
        parts.append('<g opacity="0">')
        parts.append(f'<animate attributeName="opacity" values="{";".join(vals)}" dur="4s" repeatCount="indefinite" calcMode="discrete"/>')
        for y,r,color in [(125,r50,COLORS[0]),(225,r95,COLORS[1])]:
            ww=570*r/2.6
            parts += [f'<rect x="220" y="{y-18}" width="{ww:.1f}" height="32" rx="5" fill="{color}"/>',
                      f'<text x="{230+ww:.1f}" y="{y+4}" font-size="13">{r:.2f}%</text>']
        parts += [f'<text x="450" y="305" text-anchor="middle" font-size="17">{g} post-contact generations</text>','</g>']
    parts += ['<text x="450" y="337" text-anchor="middle" font-size="11">Representative published population-model output N=7,465; independence approximation.</text>','</svg>']
    (OUT/"model10_threshold_animation.svg").write_text("\n".join(parts))


def main():
    required_rate_svg()
    isolation_svg()
    envelope_svg()
    bottleneck_svg()
    animation_svg()


if __name__ == "__main__":
    main()
