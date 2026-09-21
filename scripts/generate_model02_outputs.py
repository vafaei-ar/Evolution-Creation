"""Generate compact SVG outputs for Model 02."""

from pathlib import Path

import numpy as np

from evolution_creation.structured import (
    make_linear_migration_matrix,
    probability_of_global_fixation,
    simulate_structured_founder_spread,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)


def _line_svg(result) -> str:
    width, height = 900, 520
    left, top, plot_w, plot_h = 75, 55, 800, 400
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Founder ancestry across five demes (migration rate = 0.02)</text>',
    ]
    for frac in np.linspace(0, 1, 6):
        y = top + plot_h * (1 - frac)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="13">{frac:.1f}</text>',
        ]
    generations = np.arange(result.generations + 1)
    xs = left + plot_w * generations / result.generations
    for d in range(result.fractions_by_deme.shape[1]):
        ys = top + plot_h * (1 - result.fractions_by_deme[:, d])
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
        parts += [
            f'<polyline class="line" stroke="{palette[d]}" points="{points}"/>',
            f'<line x1="650" y1="{85 + 22 * d}" x2="680" y2="{85 + 22 * d}" stroke="{palette[d]}" stroke-width="3"/>',
            f'<text x="690" y="{90 + 22 * d}" font-size="13">Deme {d + 1}</text>',
        ]
    parts += [
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#222"/>',
        '<text x="475" y="503" text-anchor="middle" font-size="16">Generation</text>',
        '<text x="20" y="255" transform="rotate(-90 20 255)" text-anchor="middle" font-size="16">Fraction with founder ancestry</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def _heatmap_svg(grid, rates, generations) -> str:
    width, height = 900, 560
    left, top, plot_w, plot_h = 110, 65, 710, 410
    cell_w, cell_h = plot_w / len(rates), plot_h / len(generations)

    def color(value: float) -> str:
        start = np.array([68, 1, 84])
        end = np.array([253, 231, 37])
        rgb = (start + (end - start) * value).astype(int)
        return "#%02x%02x%02x" % tuple(rgb)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.cell{stroke:white;stroke-width:1}</style>',
        '<text x="450" y="32" text-anchor="middle" font-size="22">Probability of founder ancestry fixing in all demes</text>',
    ]
    for row, generation in enumerate(generations):
        y = top + (len(generations) - 1 - row) * cell_h
        parts.append(f'<text x="{left - 15}" y="{y + cell_h / 2 + 5:.1f}" text-anchor="end" font-size="13">{generation}</text>')
        for col, rate in enumerate(rates):
            x = left + col * cell_w
            value = float(grid[row, col])
            label_color = "white" if value < 0.45 else "black"
            parts += [
                f'<rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell_w:.1f}" height="{cell_h:.1f}" fill="{color(value)}"/>',
                f'<text x="{x + cell_w / 2:.1f}" y="{y + cell_h / 2 + 5:.1f}" text-anchor="middle" font-size="12" fill="{label_color}">{value:.2f}</text>',
            ]
    for col, rate in enumerate(rates):
        x = left + (col + 0.5) * cell_w
        parts.append(f'<text x="{x:.1f}" y="503" text-anchor="middle" font-size="13">{rate:g}</text>')
    parts += [
        '<text x="465" y="536" text-anchor="middle" font-size="16">Migration rate</text>',
        '<text x="25" y="270" transform="rotate(-90 25 270)" text-anchor="middle" font-size="16">Generations elapsed</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def _animated_svg(result) -> str:
    width, height = 900, 500
    left, top, plot_w, plot_h = 75, 60, 800, 370
    frames = np.arange(0, result.generations + 1, 3)
    n = result.fractions_by_deme.shape[1]
    duration = 8
    bar_w = plot_w / (n * 1.5)
    gap = (plot_w - n * bar_w) / (n + 1)
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Genealogical ancestry spreading through a chain of demes</text>',
    ]
    for frac in np.linspace(0, 1, 6):
        y = top + plot_h * (1 - frac)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="13">{frac:.1f}</text>',
        ]
    for d in range(n):
        x = left + gap + (bar_w + gap) * d
        values = result.fractions_by_deme[frames, d]
        heights = plot_h * values
        ys = top + plot_h - heights
        height_values = ";".join(f"{h:.2f}" for h in heights)
        y_values = ";".join(f"{y:.2f}" for y in ys)
        parts += [
            f'<rect x="{x:.1f}" y="{ys[0]:.2f}" width="{bar_w:.1f}" height="{heights[0]:.2f}" fill="{palette[d]}">',
            f'<animate attributeName="y" values="{y_values}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            f'<animate attributeName="height" values="{height_values}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            "</rect>",
            f'<text x="{x + bar_w / 2:.1f}" y="455" text-anchor="middle" font-size="13">{d + 1}</text>',
        ]
    parts += [
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#222"/>',
        '<text x="475" y="480" text-anchor="middle" font-size="16">Deme</text>',
        '<text x="20" y="245" transform="rotate(-90 20 245)" text-anchor="middle" font-size="16">Fraction with founder ancestry</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def main() -> None:
    trajectory = simulate_structured_founder_spread(
        deme_sizes=[300] * 5,
        generations=80,
        migration_matrix=make_linear_migration_matrix(5, 0.02),
        founder_count=10,
        seed=20260920,
    )
    (OUT / "model02_deme_spread.svg").write_text(_line_svg(trajectory))

    rates = np.array([0.0, 0.001, 0.003, 0.01, 0.03, 0.1])
    generations = np.array([10, 20, 40, 60, 80, 120])
    grid = probability_of_global_fixation(
        migration_rates=rates,
        generations=generations,
        deme_sizes=[60] * 4,
        founder_count=5,
        replicates=30,
        seed=20260920,
    )
    (OUT / "model02_fixation_heatmap.svg").write_text(_heatmap_svg(grid, rates, generations))

    animated = simulate_structured_founder_spread(
        deme_sizes=[150] * 7,
        generations=60,
        migration_matrix=make_linear_migration_matrix(7, 0.015),
        founder_count=12,
        seed=20260921,
    )
    (OUT / "model02_spread_animation.svg").write_text(_animated_svg(animated))


if __name__ == "__main__":
    main()
