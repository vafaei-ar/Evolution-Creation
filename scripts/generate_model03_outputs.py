"""Generate README SVG outputs for Model 03."""

from pathlib import Path
import numpy as np
from evolution_creation.structured import make_linear_migration_matrix
from evolution_creation.temporal import (
    make_barrier_schedule,
    make_constant_schedule,
    probability_of_global_fixation_by_barrier_timing,
    simulate_time_varying_founder_spread,
    simulate_time_varying_replicates,
)

OUT=Path("figures")
OUT.mkdir(exist_ok=True)
SEED=20260920


def write_line(path,x,series,labels):
    w,h,left,top,pw,ph=900,520,80,55,790,390
    colors=["#1f77b4","#ff7f0e","#2ca02c"]
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.g{stroke:#ddd}.c{fill:none;stroke-width:3}</style>','<text x="450" y="30" text-anchor="middle" font-size="22">Barrier timing changes global ancestry outcomes</text>']
    for k in range(6):
        f=k/5; y=top+ph*(1-f); p += [f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="13">{f:.1f}</text>']
    xmax=max(x)
    for i,vals in enumerate(series):
        pts=" ".join(f"{left+pw*xv/xmax:.1f},{top+ph*(1-yv):.1f}" for xv,yv in zip(x,vals))
        p += [f'<polyline class="c" stroke="{colors[i]}" points="{pts}"/>',f'<line x1="630" y1="{80+24*i}" x2="665" y2="{80+24*i}" stroke="{colors[i]}" stroke-width="3"/>',f'<text x="675" y="{85+24*i}" font-size="13">{labels[i]}</text>']
    for xv,label in [(1,"1"),(10,"10"),(20,"20"),(30,"30"),(40,"40"),(50,"50"),(xmax,"never")]:
        px=left+pw*xv/xmax; p.append(f'<text x="{px:.1f}" y="{top+ph+23}" text-anchor="middle" font-size="13">{label}</text>')
    p += [f'<line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" stroke="#222"/>','<text x="475" y="500" text-anchor="middle" font-size="16">Generation when permanent barrier closes</text>','<text x="20" y="250" transform="rotate(-90 20 250)" text-anchor="middle" font-size="16">P(global fixation by generation 60)</text>','<text x="450" y="518" text-anchor="middle" font-size="11">Illustrative Monte Carlo estimates; not historical migration estimates</text>','</svg>']
    path.write_text("\n".join(p))


def write_heat(path,data,labels):
    w,h,left,top,pw,ph=920,500,220,65,620,350
    rows,cols=data.shape; cw,ch=pw/cols,ph/rows
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.cell{stroke:white}</style>','<text x="460" y="30" text-anchor="middle" font-size="21">Probability each deme contains founder descendants at generation 60</text>']
    for r in range(rows):
        y=top+r*ch; p.append(f'<text x="{left-12}" y="{y+ch/2+5:.1f}" text-anchor="end" font-size="13">{labels[r]}</text>')
        for c in range(cols):
            x=left+c*cw; v=float(data[r,c]); fill="#fde725" if v>=.5 else "#440154"; tc="black" if v>=.5 else "white"
            p += [f'<rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="{fill}"/>',f'<text x="{x+cw/2:.1f}" y="{y+ch/2+5:.1f}" text-anchor="middle" font-size="13" fill="{tc}">{v:.2f}</text>']
    for c in range(cols):
        x=left+(c+.5)*cw; p.append(f'<text x="{x:.1f}" y="{top+ph+24}" text-anchor="middle" font-size="13">Deme {c+1}</text>')
    p += ['<text x="460" y="470" text-anchor="middle" font-size="12">Barrier is between Deme 3 and Deme 4. Values are illustrative simulation outputs.</text>','</svg>']
    path.write_text("\n".join(p))


def write_animation(path,result,close_at=20):
    frames=np.arange(0,result.generations+1,2); values=result.fractions_by_deme[frames]
    w,h,left,top,pw,ph=900,500,75,65,800,350; n=values.shape[1]; dur=10; bw=pw/(n*1.5); gap=(pw-n*bw)/(n+1)
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#111}.g{stroke:#ddd}</style>',f'<text x="450" y="30" text-anchor="middle" font-size="21">Barrier closes at generation {close_at}; ancestry already crossed before isolation</text>']
    for k in range(6):
        f=k/5; y=top+ph*(1-f); p += [f'<line class="g" x1="{left}" y1="{y:.1f}" x2="{left+pw}" y2="{y:.1f}"/>',f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="13">{f:.1f}</text>']
    for d in range(n):
        x=left+gap+(bw+gap)*d; heights=ph*values[:,d]; ys=top+ph-heights
        p += [f'<rect x="{x:.1f}" y="{ys[0]:.2f}" width="{bw:.1f}" height="{heights[0]:.2f}">',f'<animate attributeName="y" values="{";".join(f"{v:.2f}" for v in ys)}" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>',f'<animate attributeName="height" values="{";".join(f"{v:.2f}" for v in heights)}" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>','</rect>',f'<text x="{x+bw/2:.1f}" y="445" text-anchor="middle" font-size="13">Deme {d+1}</text>']
    bx=left+gap+(bw+gap)*3-gap/2; opacity=["0.12" if g<close_at else "1.0" for g in frames]
    p += [f'<line x1="{bx:.1f}" y1="{top}" x2="{bx:.1f}" y2="{top+ph}" stroke="#d62728" stroke-width="4" stroke-dasharray="8 6" opacity="{opacity[0]}">',f'<animate attributeName="opacity" values="{";".join(opacity)}" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>','</line>',f'<text x="{bx:.1f}" y="55" text-anchor="middle" font-size="13">barrier</text>','</svg>']
    path.write_text("\n".join(p))


def main():
    closures=np.array([1,5,10,15,20,30,40,50,61]); series=[]; labels=[]
    for offset,rate in enumerate([.005,.02,.05]):
        p=probability_of_global_fixation_by_barrier_timing(make_linear_migration_matrix(4,rate),1,closures,60,[50]*4,founder_count=6,replicates=40,seed=SEED+offset)
        series.append(p); labels.append(f"migration rate = {rate:g}")
    write_line(OUT/"model03_closure_timing.svg",closures,series,labels)

    base=make_linear_migration_matrix(6,.015); g=60
    scenarios=[("always connected",make_constant_schedule(base,g)),("closed from gen 1",make_barrier_schedule(base,g,2,1)),("closes at gen 10",make_barrier_schedule(base,g,2,10)),("closes at gen 25",make_barrier_schedule(base,g,2,25)),("closed gen 1-20",make_barrier_schedule(base,g,2,1,21))]
    data=[]
    for i,(_,schedule) in enumerate(scenarios):
        curves=simulate_time_varying_replicates([70]*6,schedule,founder_count=8,replicates=40,seed=SEED+i)
        data.append(np.mean(curves[:,-1,:]>0,axis=0))
    write_heat(OUT/"model03_scenario_heatmap.svg",np.asarray(data),[x[0] for x in scenarios])

    base=make_linear_migration_matrix(6,.02); schedule=make_barrier_schedule(base,50,2,20)
    result=simulate_time_varying_founder_spread([120]*6,schedule,founder_count=12,seed=20260923)
    write_animation(OUT/"model03_barrier_animation.svg",result,20)


if __name__=="__main__":
    main()
