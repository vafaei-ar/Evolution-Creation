"""Generate deterministic SVG outputs for Model 06."""

from pathlib import Path

import numpy as np

from evolution_creation.coalescence import (
    chang_asymptotic_generations,
    make_parent_source_matrix,
    simulate_coalescence_replicates,
    simulate_pedigree_coalescence,
    simulate_structured_pedigree_coalescence,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)
SEED = 20260920

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def _base_svg(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        f'<text x="{width/2:.0f}" y="30" text-anchor="middle" font-size="22">{title}</text>',
    ]


def scaling_svg(path):
    populations = np.array([50, 100, 200, 500, 1000, 2000])
    med_mrca, med_iap, bench_mrca, bench_iap = [], [], [], []

    for i, population in enumerate(populations):
        summary = simulate_coalescence_replicates(
            population_size=int(population),
            replicates=80,
            seed=SEED + i,
        )
        med_mrca.append(summary.median_mrca_generation)
        med_iap.append(summary.median_iap_generation)
        mrca, iap = chang_asymptotic_generations(int(population))
        bench_mrca.append(mrca)
        bench_iap.append(iap)

    med_mrca = np.asarray(med_mrca)
    med_iap = np.asarray(med_iap)
    bench_mrca = np.asarray(bench_mrca)
    bench_iap = np.asarray(bench_iap)

    width, height = 900, 520
    left, top, plot_w, plot_h = 85, 60, 750, 380
    y_max = max(30.0, float(med_iap.max()) + 3)
    logx = np.log10(populations)
    x_min, x_max = float(logx.min()), float(logx.max())

    parts = _base_svg(
        width,
        height,
        "Exact pedigree simulations versus Chang asymptotic benchmarks",
    )
    for y_value in range(0, int(y_max) + 1, 5):
        y = top + plot_h * (1 - y_value / y_max)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{y_value}</text>',
        ]

    def px(population):
        return left + plot_w * (
            np.log10(population) - x_min
        ) / (x_max - x_min)

    def py(value):
        return top + plot_h * (1 - value / y_max)

    for population in populations:
        x = px(population)
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{population}</text>'
        )

    series = [
        (med_mrca, COLORS[0], "simulation median MRCA", False),
        (med_iap, COLORS[1], "simulation median IAP", False),
        (bench_mrca, COLORS[0], "Chang MRCA ~ log2(N)", True),
        (bench_iap, COLORS[1], "Chang IAP ~ 1.77 log2(N)", True),
    ]
    for index, (values, color, label, dashed) in enumerate(series):
        points = " ".join(
            f"{px(pop):.1f},{py(value):.1f}"
            for pop, value in zip(populations, values)
        )
        dash = ' stroke-dasharray="8 6"' if dashed else ""
        parts.append(
            f'<polyline class="line" stroke="{color}"{dash} points="{points}"/>'
        )
        y_leg = 82 + 22 * index
        parts += [
            f'<line x1="560" y1="{y_leg}" x2="595" y2="{y_leg}" stroke="{color}" stroke-width="3"{dash}/>',
            f'<text x="605" y="{y_leg + 5}" font-size="12">{label}</text>',
        ]

    parts += [
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#222"/>',
        '<text x="460" y="495" text-anchor="middle" font-size="15">Population size N (log-spaced axis)</text>',
        '<text x="24" y="250" transform="rotate(-90 24 250)" text-anchor="middle" font-size="15">Generations before present</text>',
        '<text x="450" y="516" text-anchor="middle" font-size="11">80 replicates per point; finite-N simulations converge only gradually to the asymptotic benchmarks.</text>',
        "</svg>",
    ]
    path.write_text("\n".join(parts))


def status_svg(path):
    result = simulate_pedigree_coalescence(
        population_size=500,
        max_generations=30,
        seed=SEED,
        stop_at_iap=False,
    )
    x = result.generations_back
    series = [
        result.noncontributing_counts / result.population_size,
        result.partial_counts / result.population_size,
        result.universal_counts / result.population_size,
    ]
    labels = [
        "no present descendants",
        "partial ancestors",
        "universal ancestors",
    ]

    width, height = 900, 500
    left, top, plot_w, plot_h = 80, 55, 780, 350
    parts = _base_svg(
        width,
        height,
        "One exact backward pedigree: ancestor status by generation",
    )
    for k in range(6):
        frac = k / 5
        y = top + plot_h * (1 - frac)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{frac:.1f}</text>',
        ]
    for index, values in enumerate(series):
        points = " ".join(
            f"{left + plot_w * generation / x[-1]:.1f},{top + plot_h * (1 - value):.1f}"
            for generation, value in zip(x, values)
        )
        parts.append(
            f'<polyline class="line" stroke="{COLORS[index]}" points="{points}"/>'
        )
        y_leg = 80 + 22 * index
        parts += [
            f'<line x1="610" y1="{y_leg}" x2="642" y2="{y_leg}" stroke="{COLORS[index]}" stroke-width="3"/>',
            f'<text x="652" y="{y_leg + 5}" font-size="12">{labels[index]}</text>',
        ]
    if result.mrca_generation is not None:
        x_mrca = left + plot_w * result.mrca_generation / x[-1]
        parts += [
            f'<line x1="{x_mrca:.1f}" y1="{top}" x2="{x_mrca:.1f}" y2="{top + plot_h}" stroke="#666" stroke-dasharray="5 5"/>',
            f'<text x="{x_mrca + 5:.1f}" y="{top + plot_h - 8}" font-size="12">MRCA = {result.mrca_generation}</text>',
        ]
    if result.iap_generation is not None:
        x_iap = left + plot_w * result.iap_generation / x[-1]
        parts += [
            f'<line x1="{x_iap:.1f}" y1="{top}" x2="{x_iap:.1f}" y2="{top + plot_h}" stroke="#111" stroke-dasharray="8 5"/>',
            f'<text x="{x_iap + 5:.1f}" y="{top + plot_h - 25}" font-size="12">IAP = {result.iap_generation}</text>',
        ]
    parts += [
        '<text x="470" y="445" text-anchor="middle" font-size="15">Generations before present</text>',
        '<text x="22" y="230" transform="rotate(-90 22 230)" text-anchor="middle" font-size="15">Fraction of past generation</text>',
        '<text x="450" y="480" text-anchor="middle" font-size="11">N = 500, seed = 20260920. MRCA is the first universal ancestor; IAP is when no partial ancestors remain.</text>',
        "</svg>",
    ]
    path.write_text("\n".join(parts))


def isolation_svg(path):
    sizes = [100] * 4
    strengths = [0.0, 0.5, 0.9, 0.98, 0.995, 1.0]
    med_mrca, med_iap = [], []

    for i, strength in enumerate(strengths):
        matrix = make_parent_source_matrix(sizes, strength)
        mrca_values, iap_values = [], []
        for replicate in range(40):
            result = simulate_structured_pedigree_coalescence(
                community_sizes=sizes,
                parent_source_matrix=matrix,
                max_generations=100,
                seed=SEED + i * 1000 + replicate,
            )
            if result.mrca_generation is not None:
                mrca_values.append(result.mrca_generation)
            if result.iap_generation is not None:
                iap_values.append(result.iap_generation)
        med_mrca.append(
            float(np.median(mrca_values))
            if mrca_values else np.nan
        )
        med_iap.append(
            float(np.median(iap_values))
            if iap_values else np.nan
        )

    width, height = 900, 520
    left, top, plot_w, plot_h = 90, 60, 740, 360
    y_max = 45
    parts = _base_svg(
        width,
        height,
        "Population structure delays coalescence; complete isolation prevents it",
    )
    for y_value in range(0, y_max + 1, 5):
        y = top + plot_h * (1 - y_value / y_max)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{y_value}</text>',
        ]
    step = plot_w / (len(strengths) - 1)
    xs = [left + i * step for i in range(len(strengths))]
    for x_value, strength in zip(xs, strengths):
        parts.append(
            f'<text x="{x_value:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{strength:g}</text>'
        )

    for values, color in [
        (med_mrca, COLORS[0]),
        (med_iap, COLORS[1]),
    ]:
        finite_points = [
            (
                x_value,
                top + plot_h * (1 - value / y_max),
            )
            for x_value, value in zip(xs, values)
            if np.isfinite(value)
        ]
        points = " ".join(
            f"{x:.1f},{y:.1f}"
            for x, y in finite_points
        )
        parts.append(
            f'<polyline class="line" stroke="{color}" points="{points}"/>'
        )
    parts += [
        f'<line x1="575" y1="82" x2="610" y2="82" stroke="{COLORS[0]}" stroke-width="3"/>',
        '<text x="620" y="87" font-size="12">median MRCA</text>',
        f'<line x1="575" y1="105" x2="610" y2="105" stroke="{COLORS[1]}" stroke-width="3"/>',
        '<text x="620" y="110" font-size="12">median IAP</text>',
        f'<text x="{xs[-1]:.1f}" y="{top + 55}" text-anchor="middle" font-size="12">not reached</text>',
        '<text x="460" y="475" text-anchor="middle" font-size="15">Community isolation strength</text>',
        '<text x="24" y="240" transform="rotate(-90 24 240)" text-anchor="middle" font-size="15">Generations before present</text>',
        '<text x="450" y="505" text-anchor="middle" font-size="11">Four communities of 100; 40 replicates per setting. At isolation = 1, no global MRCA exists in the simulated pedigree.</text>',
        "</svg>",
    ]
    path.write_text("\n".join(parts))


def animation_svg(path):
    result = simulate_pedigree_coalescence(
        population_size=300,
        max_generations=30,
        seed=20260926,
        stop_at_iap=True,
    )
    fractions = np.column_stack(
        [
            result.noncontributing_counts / result.population_size,
            result.partial_counts / result.population_size,
            result.universal_counts / result.population_size,
        ]
    )
    labels = ["No descendants", "Partial", "Universal"]

    width, height = 900, 500
    top, bottom = 70, 390
    xs = [145, 375, 605]
    bar_w = 155
    duration = 10
    parts = _base_svg(
        width,
        height,
        "Backward pedigree transition from partial to universal ancestors",
    )
    for k in range(6):
        frac = k / 5
        y = bottom - (bottom - top) * frac
        parts += [
            f'<line class="grid" x1="80" y1="{y:.1f}" x2="835" y2="{y:.1f}"/>',
            f'<text x="68" y="{y + 5:.1f}" text-anchor="end" font-size="12">{frac:.1f}</text>',
        ]
    for index in range(3):
        heights = (bottom - top) * fractions[:, index]
        ys = bottom - heights
        parts += [
            f'<rect x="{xs[index]}" y="{ys[0]:.2f}" width="{bar_w}" height="{heights[0]:.2f}" fill="{COLORS[index]}">',
            f'<animate attributeName="y" values="{";".join(f"{v:.2f}" for v in ys)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            f'<animate attributeName="height" values="{";".join(f"{v:.2f}" for v in heights)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            "</rect>",
            f'<text x="{xs[index] + bar_w / 2:.1f}" y="420" text-anchor="middle" font-size="13">{labels[index]}</text>',
        ]
    parts += [
        '<text x="450" y="455" text-anchor="middle" font-size="12">One N = 300 stochastic pedigree; animation stops when the IAP is reached.</text>',
        "</svg>",
    ]
    path.write_text("\n".join(parts))


def main():
    scaling_svg(OUT / "model06_scaling.svg")
    status_svg(OUT / "model06_status_trajectory.svg")
    isolation_svg(OUT / "model06_isolation_sensitivity.svg")
    animation_svg(OUT / "model06_status_animation.svg")


if __name__ == "__main__":
    main()
