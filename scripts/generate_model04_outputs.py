"""Generate README SVG outputs for Model 04."""

from pathlib import Path
import math

OUT=Path("figures")
OUT.mkdir(exist_ok=True)


def logistic(n0,k,r,t):
    if k==n0:
        return float(n0)
    return k/(1+((k-n0)/n0)*math.exp(-r*t))


def ancestry_fraction(f0,t):
    return 1-(1-f0)**(2**t)


def overlap_fractions(f0,tmax):
    founder_only=f0
    background_only=1-f0
    both=0.0
    out=[]
    for _ in range(tmax+1):
        out.append((founder_only,background_only,both))
        next_founder_only=founder_only**2
        next_background_only=background_only**2
        next_both=1-next_founder_only-next_background_only
        founder_only,background_only,both=next_founder_only,next_background_only,next_both
    return out


def write_demography(path):
    w,h=900,650
    left,right=85,860
    top1,bottom1=55,290
    top2,bottom2=355,590
    gens=list(range(17))
    constant=[1000 for _ in gens]
    exponential=[1000*math.exp(.10*t) for t in gens]
    logistic_values=[logistic(1000,5000,.30,t) for t in gens]
    fraction=[ancestry_fraction(.001,t) for t in gens]
    colors=["#1f77b4","#ff7f0e","#2ca02c"]

    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.g{stroke:#ddd}.l{fill:none;stroke-width:3}</style>','<text x="450" y="28" text-anchor="middle" font-size="22">Population growth changes counts, not the neutral ancestry-fraction recurrence</text>']

    max_n=5200
    for k in range(6):
        value=k*1000
        y=bottom1-(bottom1-top1)*value/max_n
        p += [f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}"/>',f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{value}</text>']

    for i,vals in enumerate([constant,exponential,logistic_values]):
        pts=" ".join(f"{left+(right-left)*t/16:.1f},{bottom1-(bottom1-top1)*v/max_n:.1f}" for t,v in zip(gens,vals))
        p.append(f'<polyline class="l" stroke="{colors[i]}" points="{pts}"/>')

    names=["constant N = 1000","exponential r = 0.10","logistic K = 5000"]
    for i,name in enumerate(names):
        y=80+23*i
        p += [f'<line x1="615" y1="{y}" x2="650" y2="{y}" stroke="{colors[i]}" stroke-width="3"/>',f'<text x="660" y="{y+5}" font-size="12">{name}</text>']

    p.append('<text x="25" y="175" transform="rotate(-90 25 175)" text-anchor="middle" font-size="15">Population size</text>')

    for k in range(6):
        value=k/5
        y=bottom2-(bottom2-top2)*value
        p += [f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}"/>',f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>']

    pts=" ".join(f"{left+(right-left)*t/16:.1f},{bottom2-(bottom2-top2)*v:.1f}" for t,v in zip(gens,fraction))
    p += [f'<polyline class="l" stroke="#222" points="{pts}"/>','<text x="610" y="390" font-size="13">all three demographic schedules coincide</text>','<text x="25" y="475" transform="rotate(-90 25 475)" text-anchor="middle" font-size="15">Founder-descendant fraction</text>']

    for t in [0,4,8,12,16]:
        x=left+(right-left)*t/16
        p.append(f'<text x="{x:.1f}" y="620" text-anchor="middle" font-size="12">{t}</text>')
    p += ['<text x="475" y="642" text-anchor="middle" font-size="15">Generation</text>','</svg>']
    path.write_text("\n".join(p))


def write_overlap(path):
    w,h=900,500
    left,top,pw,ph=80,55,780,360
    data=overlap_fractions(.001,13)
    founder=[a+c for a,b,c in data]
    background=[b+c for a,b,c in data]
    both=[c for a,b,c in data]
    colors=["#1f77b4","#ff7f0e","#2ca02c"]
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.g{stroke:#ddd}.l{fill:none;stroke-width:3}</style>','<text x="450" y="28" text-anchor="middle" font-size="22">Descendant sets overlap after intermarriage</text>']
    for k in range(6):
        value=k/5; y=top+ph*(1-value)
        p += [f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>']
    for i,vals in enumerate([founder,background,both]):
        pts=" ".join(f"{left+pw*t/13:.1f},{top+ph*(1-v):.1f}" for t,v in enumerate(vals))
        p.append(f'<polyline class="l" stroke="{colors[i]}" points="{pts}"/>')
    names=["descendants of founder","descendants of background","descendants of both"]
    for i,name in enumerate(names):
        y=80+23*i
        p += [f'<line x1="600" y1="{y}" x2="635" y2="{y}" stroke="{colors[i]}" stroke-width="3"/>',f'<text x="645" y="{y+5}" font-size="12">{name}</text>']
    for t in [0,2,4,6,8,10,12]:
        x=left+pw*t/13
        p.append(f'<text x="{x:.1f}" y="445" text-anchor="middle" font-size="12">{t}</text>')
    p += ['<text x="470" y="475" text-anchor="middle" font-size="15">Generation</text>','<text x="23" y="235" transform="rotate(-90 23 235)" text-anchor="middle" font-size="15">Fraction of population</text>','<text x="450" y="495" text-anchor="middle" font-size="11">The two descendant sets are not mutually exclusive; their sum can exceed 1.</text>','</svg>']
    path.write_text("\n".join(p))


def write_animation(path):
    data=overlap_fractions(.001,13)
    values=[
        [a+c for a,b,c in data],
        [b+c for a,b,c in data],
        [c for a,b,c in data],
    ]
    labels=["Founder descendants","Background descendants","Both"]
    colors=["#1f77b4","#ff7f0e","#2ca02c"]
    w,h=900,500
    top,bottom=70,390
    bar_w=150
    xs=[150,375,600]
    duration=9
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.g{stroke:#ddd}</style>','<text x="450" y="30" text-anchor="middle" font-size="22">Overlapping genealogical descendant sets</text>','<text x="450" y="52" text-anchor="middle" font-size="12">These bars are overlapping sets, not pieces of one partition.</text>']
    for k in range(6):
        frac=k/5; y=bottom-(bottom-top)*frac
        p += [f'<line class="g" x1="80" y1="{y:.1f}" x2="830" y2="{y:.1f}"/>',f'<text x="68" y="{y+5:.1f}" text-anchor="end" font-size="12">{frac:.1f}</text>']
    for i,vals in enumerate(values):
        heights=[(bottom-top)*v for v in vals]
        ys=[bottom-h for h in heights]
        p += [f'<rect x="{xs[i]}" y="{ys[0]:.2f}" width="{bar_w}" height="{heights[0]:.2f}" fill="{colors[i]}">',f'<animate attributeName="y" values="{";".join(f"{v:.2f}" for v in ys)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',f'<animate attributeName="height" values="{";".join(f"{v:.2f}" for v in heights)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>','</rect>',f'<text x="{xs[i]+bar_w/2}" y="420" text-anchor="middle" font-size="13">{labels[i]}</text>']
    p += ['</svg>']
    path.write_text("\n".join(p))


def main():
    write_demography(OUT/"model04_demography_vs_fraction.svg")
    write_overlap(OUT/"model04_overlapping_descendants.svg")
    write_animation(OUT/"model04_overlap_animation.svg")


if __name__=="__main__":
    main()
