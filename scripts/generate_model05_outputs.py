"""Generate deterministic SVG outputs for Model 05."""

from pathlib import Path
import numpy as np

from evolution_creation.assortment import (
    deterministic_endogamy_curve,
    make_endogamy_matrix,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)


def line_svg(path):
    sizes = [500] * 4
    strengths = [0.0, 0.5, 0.9, 0.98, 1.0]
    generations = 40
    curves = []
    for strength in strengths:
        matrix = make_endogamy_matrix(sizes, strength)
        result = deterministic_endogamy_curve(
            sizes,
            generations,
            matrix,
            founder_count=10,
        )
        curves.append(result[:, -1])

    width, height = 900, 500
    left, top, plot_w, plot_h = 80, 55, 780, 360
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="450" y="28" text-anchor="middle" font-size="22">Founder ancestry reaching the last community</text>',
    ]
    for k in range(6):
        value = k / 5
        y = top + plot_h * (1 - value)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>',
        ]
    x = np.arange(generations + 1)
    for i, values in enumerate(curves):
        points = " ".join(
            f"{left + plot_w * g / generations:.1f},{top + plot_h * (1 - v):.1f}"
            for g, v in zip(x, values)
        )
        parts += [
            f'<polyline class="line" stroke="{colors[i]}" points="{points}"/>',
            f'<line x1="610" y1="{78 + 22 * i}" x2="642" y2="{78 + 22 * i}" stroke="{colors[i]}" stroke-width="3"/>',
            f'<text x="652" y="{83 + 22 * i}" font-size="12">endogamy = {strengths[i]:g}</text>',
        ]
    parts += [
        '<text x="470" y="475" text-anchor="middle" font-size="15">Generation</text>',
        '<text x="22" y="235" transform="rotate(-90 22 235)" text-anchor="middle" font-size="15">Founder-descendant fraction in Community 4</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def heatmap_svg(path):
    sizes = [500] * 4
    endogamy_values = [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 1.0]
    state_weights = [0.5, 1.0, 2.0, 5.0, 10.0]
    generation = 25
    data = np.empty((len(state_weights), len(endogamy_values)))

    for r, weight in enumerate(state_weights):
        for c, strength in enumerate(endogamy_values):
            matrix = make_endogamy_matrix(sizes, strength)
            result = deterministic_endogamy_curve(
                sizes,
                generation,
                matrix,
                founder_count=10,
                same_state_weight=weight,
            )
            data[r, c] = result[-1, -1]

    width, height = 920, 500
    left, top, plot_w, plot_h = 140, 65, 700, 330
    cell_w = plot_w / len(endogamy_values)
    cell_h = plot_h / len(state_weights)

    def color(value):
        start = np.array([68, 1, 84])
        end = np.array([253, 231, 37])
        rgb = (start + (end - start) * value).astype(int)
        return "#%02x%02x%02x" % tuple(rgb)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.cell{stroke:white}</style>',
        '<text x="460" y="30" text-anchor="middle" font-size="21">Community 4 founder-ancestry fraction after 25 generations</text>',
    ]

    for r, weight in enumerate(state_weights):
        y = top + r * cell_h
        parts.append(f'<text x="{left - 12}" y="{y + cell_h / 2 + 5:.1f}" text-anchor="end" font-size="13">{weight:g}</text>')
        for c, strength in enumerate(endogamy_values):
            x = left + c * cell_w
            value = float(data[r, c])
            text_color = "white" if value < 0.45 else "black"
            parts += [
                f'<rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell_w:.1f}" height="{cell_h:.1f}" fill="{color(value)}"/>',
                f'<text x="{x + cell_w / 2:.1f}" y="{y + cell_h / 2 + 5:.1f}" text-anchor="middle" font-size="12" fill="{text_color}">{value:.2f}</text>',
            ]

    for c, strength in enumerate(endogamy_values):
        x = left + (c + 0.5) * cell_w
        parts.append(f'<text x="{x:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{strength:g}</text>')

    parts += [
        '<text x="490" y="440" text-anchor="middle" font-size="15">Endogamy strength</text>',
        '<text x="28" y="230" transform="rotate(-90 28 230)" text-anchor="middle" font-size="15">Same-state mate weight</text>',
        '<text x="460" y="478" text-anchor="middle" font-size="11">Same-state weighting is an abstract sensitivity experiment, not a historical estimate.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def animation_svg(path):
    sizes = [300] * 5
    generations = 50
    matrix = make_endogamy_matrix(sizes, 0.97)
    result = deterministic_endogamy_curve(
        sizes,
        generations,
        matrix,
        founder_count=15,
    )
    frames = np.arange(0, generations + 1, 2)
    values = result[frames]

    width, height = 900, 500
    left, top, plot_w, plot_h = 75, 65, 800, 340
    n = values.shape[1]
    bar_w = plot_w / (n * 1.5)
    gap = (plot_w - n * bar_w) / (n + 1)
    duration = 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="21">Slow ancestry spread under strong community endogamy</text>',
        '<text x="450" y="50" text-anchor="middle" font-size="12">endogamy = 0.97; same-state weight = 1</text>',
    ]

    for k in range(6):
        frac = k / 5
        y = top + plot_h * (1 - frac)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{frac:.1f}</text>',
        ]

    for community in range(n):
        x = left + gap + (bar_w + gap) * community
        heights = plot_h * values[:, community]
        ys = top + plot_h - heights
        parts += [
            f'<rect x="{x:.1f}" y="{ys[0]:.2f}" width="{bar_w:.1f}" height="{heights[0]:.2f}">',
            f'<animate attributeName="y" values="{";".join(f"{v:.2f}" for v in ys)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            f'<animate attributeName="height" values="{";".join(f"{v:.2f}" for v in heights)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            '</rect>',
            f'<text x="{x + bar_w / 2:.1f}" y="435" text-anchor="middle" font-size="12">Community {community + 1}</text>',
        ]

    parts += [
        '<text x="22" y="235" transform="rotate(-90 22 235)" text-anchor="middle" font-size="15">Founder-descendant fraction</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def main():
    line_svg(OUT / "model05_endogamy_trajectories.svg")
    heatmap_svg(OUT / "model05_endogamy_assortment_heatmap.svg")
    animation_svg(OUT / "model05_endogamy_animation.svg")


if __name__ == "__main__":
    main()
