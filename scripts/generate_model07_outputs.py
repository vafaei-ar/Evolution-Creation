"""Generate README SVG outputs for Model 07."""

from pathlib import Path

import numpy as np

from evolution_creation.genetic_ancestry import (
    coop_genetic_ancestor_probability,
    expected_genetic_ancestor_count,
    simulate_path_replicates,
    simulate_segment_history,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)
SEED = 20260920

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


def probability_svg(path: Path) -> None:
    max_generation = 18
    summary = simulate_path_replicates(
        max_generations=max_generation,
        detectable_threshold_cm=6.0,
        replicates=4000,
        seed=SEED,
    )
    generations = summary.generations
    analytic = np.array([
        coop_genetic_ancestor_probability(int(k))
        for k in generations
    ])

    width, height = 900, 520
    left, top, plot_w, plot_h = 80, 60, 770, 370
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">A genealogical ancestor can leave no autosomal DNA</text>',
    ]

    for k in range(6):
        value = k / 5
        y = top + plot_h * (1 - value)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>',
        ]

    def px(generation: int) -> float:
        return left + plot_w * (generation - 1) / (max_generation - 1)

    def py(value: float) -> float:
        return top + plot_h * (1 - value)

    series = [
        (analytic, COLORS[0], "Poisson-fragment approximation", ' stroke-dasharray="8 6"'),
        (summary.any_dna_probability, COLORS[1], "segment simulation: any DNA", ""),
        (summary.detectable_probability, COLORS[2], "segment simulation: >= 6 cM", ""),
    ]
    for index, (values, color, label, dash) in enumerate(series):
        points = " ".join(
            f"{px(int(generation)):.1f},{py(float(value)):.1f}"
            for generation, value in zip(generations, values)
        )
        parts.append(
            f'<polyline class="line" stroke="{color}"{dash} points="{points}"/>'
        )
        y_leg = 82 + 23 * index
        parts += [
            f'<line x1="535" y1="{y_leg}" x2="570" y2="{y_leg}" stroke="{color}" stroke-width="3"{dash}/>',
            f'<text x="580" y="{y_leg + 5}" font-size="12">{label}</text>',
        ]

    for generation in [1, 4, 8, 12, 16, 18]:
        x = px(generation)
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{generation}</text>'
        )

    p8 = coop_genetic_ancestor_probability(8)
    p16 = coop_genetic_ancestor_probability(16)
    parts += [
        f'<circle cx="{px(8):.1f}" cy="{py(p8):.1f}" r="4" fill="{COLORS[0]}"/>',
        f'<text x="{px(8) + 8:.1f}" y="{py(p8) - 8:.1f}" font-size="12">p8 = {p8:.4f}</text>',
        f'<circle cx="{px(16):.1f}" cy="{py(p16):.1f}" r="4" fill="{COLORS[0]}"/>',
        f'<text x="{px(16) - 115:.1f}" y="{py(p16) - 8:.1f}" font-size="12">p16 = {p16:.4f}</text>',
        '<text x="465" y="480" text-anchor="middle" font-size="15">Generations from genealogical ancestor to descendant</text>',
        '<text x="22" y="245" transform="rotate(-90 22 245)" text-anchor="middle" font-size="15">Probability of inherited autosomal material</text>',
        '<text x="450" y="508" text-anchor="middle" font-size="11">4000 Monte Carlo paths; 6 cM is an illustrative detection threshold, not a universal testing cutoff.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def ancestor_count_svg(path: Path) -> None:
    generations = np.arange(1, 21)
    genealogical = np.array([2 ** int(k) for k in generations], dtype=float)
    genetic = np.array([
        expected_genetic_ancestor_count(int(k))
        for k in generations
    ])

    width, height = 900, 520
    left, top, plot_w, plot_h = 85, 60, 760, 370
    y_min, y_max = 0.0, 6.2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Genealogical slots grow exponentially; expected genetic ancestors do not</text>',
    ]

    for exponent in range(0, 7):
        y = top + plot_h * (1 - (exponent - y_min) / (y_max - y_min))
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">10^{exponent}</text>',
        ]

    def px(generation: int) -> float:
        return left + plot_w * (generation - 1) / 19

    def py(value: float) -> float:
        log_value = np.log10(value)
        return top + plot_h * (1 - (log_value - y_min) / (y_max - y_min))

    for values, color, label in [
        (genealogical, COLORS[0], "genealogical pedigree slots = 2^k"),
        (genetic, COLORS[1], "expected genetic ancestors"),
    ]:
        points = " ".join(
            f"{px(int(generation)):.1f},{py(float(value)):.1f}"
            for generation, value in zip(generations, values)
        )
        parts.append(
            f'<polyline class="line" stroke="{color}" points="{points}"/>'
        )
    parts += [
        f'<line x1="545" y1="83" x2="580" y2="83" stroke="{COLORS[0]}" stroke-width="3"/>',
        '<text x="590" y="88" font-size="12">genealogical pedigree slots = 2^k</text>',
        f'<line x1="545" y1="106" x2="580" y2="106" stroke="{COLORS[1]}" stroke-width="3"/>',
        '<text x="590" y="111" font-size="12">expected genetic ancestors</text>',
    ]

    for generation in [1, 4, 8, 12, 16, 20]:
        parts.append(
            f'<text x="{px(generation):.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{generation}</text>'
        )
    parts += [
        '<text x="465" y="480" text-anchor="middle" font-size="15">Generations back</text>',
        '<text x="22" y="245" transform="rotate(-90 22 245)" text-anchor="middle" font-size="15">Count (log10 scale)</text>',
        '<text x="450" y="508" text-anchor="middle" font-size="11">Expected genetic count = 2^k times the single-ancestor genetic-contribution probability; pedigree collapse is ignored.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def segment_animation_svg(path: Path) -> None:
    max_generation = 13
    history = simulate_segment_history(
        max_generations=max_generation,
        seed=20260922,
    )
    lengths = history.chromosome_lengths_morgans
    selected = [0, 3, 6, 9, 12, 15, 18, 21]
    width, height = 900, 385
    left = 155
    bar_width = 650
    top = 80
    row_height = 29
    duration = 13

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.base{fill:#e6e6e6}.founder{fill:#ff7f0e}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">One genealogical path: founder-derived autosomal segments are broken up and lost</text>',
        '<text x="450" y="52" text-anchor="middle" font-size="12">Eight representative autosomes from the 22-autosome, 33-Morgan model; seed = 20260922</text>',
    ]

    for row, chromosome_index in enumerate(selected):
        chromosome = chromosome_index + 1
        y = top + row * row_height
        parts += [
            f'<text x="{left - 12}" y="{y + 10}" text-anchor="end" font-size="11">chr {chromosome}</text>',
            f'<rect class="base" x="{left}" y="{y}" width="{bar_width}" height="12" rx="4"/>',
        ]

    for frame_index, generation_segments in enumerate(history.segments_by_generation):
        values = ["0"] * max_generation
        values[frame_index] = "1"
        parts.append('<g opacity="0">')
        parts.append(
            f'<animate attributeName="opacity" values="{";".join(values)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>'
        )
        parts.append(
            f'<text x="450" y="329" text-anchor="middle" font-size="16">Generation {frame_index + 1}</text>'
        )
        for row, chromosome_index in enumerate(selected):
            chromosome_segments = generation_segments[chromosome_index]
            y = top + row * row_height
            length = float(lengths[chromosome_index])
            for start, end in chromosome_segments:
                x = left + bar_width * start / length
                segment_width = bar_width * (end - start) / length
                parts.append(
                    f'<rect class="founder" x="{x:.2f}" y="{y}" width="{segment_width:.2f}" height="12" rx="3"/>'
                )
        parts.append('</g>')

    parts += [
        '<text x="450" y="357" text-anchor="middle" font-size="11">Orange = DNA inherited from the focal genealogical ancestor along this one path.</text>',
        '<text x="450" y="374" text-anchor="middle" font-size="11">Only selected autosomes are displayed; the full 22-autosome state is used in the simulation.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def main() -> None:
    probability_svg(OUT / "model07_genetic_probability.svg")
    ancestor_count_svg(OUT / "model07_ancestor_counts.svg")
    segment_animation_svg(OUT / "model07_segment_animation.svg")


if __name__ == "__main__":
    main()
