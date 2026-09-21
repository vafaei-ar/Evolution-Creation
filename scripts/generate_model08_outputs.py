"""Generate deterministic SVG outputs for Model 08."""

from pathlib import Path

import numpy as np

from evolution_creation.pedigree_genome import (
    simulate_pedigree_genome,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

POPULATION_SIZE = 500
FOUNDER_COUNT = 2
MAX_GENERATIONS = 30
THRESHOLD_CM = 6.0
SEED = 3

COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
]


def _result():
    return simulate_pedigree_genome(
        population_size=POPULATION_SIZE,
        max_generations=MAX_GENERATIONS,
        founder_count=FOUNDER_COUNT,
        detectable_threshold_cm=THRESHOLD_CM,
        distinct_parents=True,
        seed=SEED,
    )


def joint_trajectory_svg(path: Path) -> None:
    result = _result()
    width, height = 900, 520
    left, top, plot_w, plot_h = 80, 60, 770, 370

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Genealogical universality and genetic carriage are different events</text>',
    ]

    for tick in range(6):
        value = tick / 5
        y = top + plot_h * (1 - value)
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>',
        ]

    def px(generation: int) -> float:
        return left + plot_w * generation / MAX_GENERATIONS

    def py(value: float) -> float:
        return top + plot_h * (1 - value)

    series = [
        (
            result.any_founder_descendant_fraction,
            COLORS[0],
            "descendant of >=1 founder",
            "",
        ),
        (
            result.all_founders_descendant_fraction,
            COLORS[1],
            "descendant of both founders",
            "",
        ),
        (
            result.genetic_carrier_fraction,
            COLORS[2],
            "any founder-set autosomal DNA",
            "",
        ),
        (
            result.detectable_carrier_fraction,
            COLORS[3],
            ">= 6 cM founder segment",
            ' stroke-dasharray="8 5"',
        ),
    ]

    for index, (values, color, label, dash) in enumerate(series):
        points = " ".join(
            f"{px(int(generation)):.1f},{py(float(value)):.1f}"
            for generation, value in zip(result.generations, values)
        )
        parts.append(
            f'<polyline class="line" stroke="{color}"{dash} points="{points}"/>'
        )
        legend_y = 82 + 22 * index
        parts += [
            f'<line x1="535" y1="{legend_y}" x2="570" y2="{legend_y}" stroke="{color}" stroke-width="3"{dash}/>',
            f'<text x="580" y="{legend_y + 5}" font-size="12">{label}</text>',
        ]

    universal = result.all_founders_universal_generation
    if universal is not None:
        x = px(universal)
        parts += [
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="#555" stroke-dasharray="4 5"/>',
            f'<text x="{x + 7:.1f}" y="{top + plot_h - 12}" font-size="12">both universal: generation {universal}</text>',
        ]

    for generation in [0, 5, 10, 15, 20, 25, 30]:
        x = px(generation)
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 24}" text-anchor="middle" font-size="12">{generation}</text>'
        )

    parts += [
        '<text x="465" y="480" text-anchor="middle" font-size="15">Generation</text>',
        '<text x="22" y="245" transform="rotate(-90 22 245)" text-anchor="middle" font-size="15">Population fraction</text>',
        '<text x="450" y="508" text-anchor="middle" font-size="11">Illustrative stochastic run: N=500, two founders, seed=3, distinct parents, 6 cM threshold.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def category_bars_svg(path: Path) -> None:
    result = _result()
    generations = [13, 20, 30]
    width, height = 900, 500
    left, top, plot_h = 110, 65, 330
    bar_width = 150
    gap = 95
    baseline = top + plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">After both founders become universal, genetic status can still differ</text>',
    ]

    for tick in range(6):
        value = tick / 5
        y = baseline - plot_h * value
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="830" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{value:.1f}</text>',
        ]

    labels = [
        ("all founders, no DNA", COLORS[0]),
        ("all founders, < 6 cM", COLORS[1]),
        ("all founders, >= 6 cM", COLORS[2]),
    ]

    for index, generation in enumerate(generations):
        x = left + 90 + index * (bar_width + gap)
        values = [
            result.all_founders_no_dna_fraction[generation],
            result.all_founders_subdetectable_fraction[generation],
            result.all_founders_detectable_fraction[generation],
        ]
        y_bottom = baseline
        for value, (_label, color) in zip(values, labels):
            height_px = plot_h * float(value)
            y = y_bottom - height_px
            parts.append(
                f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{height_px:.1f}" fill="{color}"/>'
            )
            y_bottom = y
        parts.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{baseline + 26}" text-anchor="middle" font-size="13">generation {generation}</text>'
        )

    for index, (label, color) in enumerate(labels):
        y = 78 + index * 23
        parts += [
            f'<rect x="555" y="{y - 11}" width="18" height="12" fill="{color}"/>',
            f'<text x="582" y="{y}" font-size="12">{label}</text>',
        ]

    universal = result.all_founders_universal_generation
    parts += [
        '<text x="470" y="463" text-anchor="middle" font-size="12">Bars are conditional categories of the whole population; both founders are universal by generation '
        + str(universal)
        + ' in this run.</text>',
        '<text x="22" y="230" transform="rotate(-90 22 230)" text-anchor="middle" font-size="15">Population fraction</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def category_animation_svg(path: Path) -> None:
    result = _result()
    generations = list(range(MAX_GENERATIONS + 1))
    width, height = 900, 430
    left, top = 190, 75
    bar_width, bar_height = 540, 235
    duration = 15

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Population states as genealogy spreads and founder DNA recombines</text>',
        f'<rect x="{left}" y="{top}" width="{bar_width}" height="{bar_height}" fill="#f5f5f5"/>',
    ]

    categories = [
        (
            result.not_all_founders_fraction,
            "#bbbbbb",
            "not descended from both founders",
        ),
        (
            result.all_founders_no_dna_fraction,
            COLORS[0],
            "both founders, no founder DNA",
        ),
        (
            result.all_founders_subdetectable_fraction,
            COLORS[1],
            "both founders, founder DNA < 6 cM",
        ),
        (
            result.all_founders_detectable_fraction,
            COLORS[2],
            "both founders, founder DNA >= 6 cM",
        ),
    ]

    for frame, generation in enumerate(generations):
        values = ["0"] * len(generations)
        values[frame] = "1"
        parts.append('<g opacity="0">')
        parts.append(
            f'<animate attributeName="opacity" values="{";".join(values)}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>'
        )
        x = left
        for series, color, _label in categories:
            fraction = float(series[generation])
            width_px = bar_width * fraction
            if width_px > 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{top}" width="{width_px:.1f}" height="{bar_height}" fill="{color}"/>'
                )
            x += width_px
        parts.append(
            f'<text x="450" y="340" text-anchor="middle" font-size="17">generation {generation}</text>'
        )
        parts.append('</g>')

    for index, (_series, color, label) in enumerate(categories):
        y = 372 + (index % 2) * 24
        x = 95 + (index // 2) * 405
        parts += [
            f'<rect x="{x}" y="{y - 12}" width="18" height="12" fill="{color}"/>',
            f'<text x="{x + 27}" y="{y}" font-size="12">{label}</text>',
        ]

    parts += [
        '<text x="450" y="55" text-anchor="middle" font-size="11">N=500, two founders, seed=3. Width shows fraction of the whole population.</text>',
        '</svg>',
    ]
    path.write_text("\n".join(parts))


def main() -> None:
    joint_trajectory_svg(
        OUT / "model08_joint_trajectory.svg"
    )
    category_bars_svg(
        OUT / "model08_universal_categories.svg"
    )
    category_animation_svg(
        OUT / "model08_category_animation.svg"
    )


if __name__ == "__main__":
    main()
