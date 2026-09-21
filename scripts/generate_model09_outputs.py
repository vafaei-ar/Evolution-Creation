"""Generate deterministic SVG outputs for Model 09."""

from pathlib import Path

import numpy as np

from evolution_creation.historical_constraints import (
    deterministic_historical_genealogy,
    make_debate_historical_scenario,
    simulate_late_contact_sensitivity,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
]


def timeline_svg(path: Path) -> None:
    width, height = 950, 430
    left, right = 120, 880
    axis_y = 235
    max_age = 60_000
    events = [
        (
            52_000,
            "Sahul settled",
            "conservative 47.5-55 ka range",
        ),
        (
            15_000,
            "Americas occupied",
            "at least ~15 ka",
        ),
        (
            12_000,
            "Tasmania separated",
            "Bassian land bridge ~12 ka",
        ),
        (
            11_000,
            "Proposed founders",
            "debate: ~11 ka, West Asia",
        ),
        (
            223,
            "Permanent European settlement",
            "Tasmania, 1803 CE",
        ),
        (
            0,
            "Present",
            "2026 CE",
        ),
    ]

    def px(age):
        return right - (
            age
            / max_age
        ) * (
            right
            - left
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.axis{stroke:#222;stroke-width:2}.tick{stroke:#666}</style>',
        '<text x="475" y="30" text-anchor="middle" font-size="22">Historical constraints around an 11,000-year founder date</text>',
        f'<line class="axis" x1="{left}" y1="{axis_y}" x2="{right}" y2="{axis_y}"/>',
    ]

    for age in [
        60_000,
        50_000,
        40_000,
        30_000,
        20_000,
        10_000,
        0,
    ]:
        x = px(age)
        label = (
            "present"
            if age == 0
            else f"{age//1000} ka"
        )
        parts += [
            f'<line class="tick" x1="{x:.1f}" y1="{axis_y-6}" x2="{x:.1f}" y2="{axis_y+6}"/>',
            f'<text x="{x:.1f}" y="{axis_y+27}" text-anchor="middle" font-size="12">{label}</text>',
        ]

    lanes = [
        95,
        135,
        175,
        295,
        335,
        375,
    ]

    for event_index, (
        age,
        label,
        detail,
    ) in enumerate(events):
        y = lanes[
            event_index
        ]
        x = px(
            age
        )
        above = (
            y
            < axis_y
        )
        y_line = (
            axis_y
            - 12
            if above
            else axis_y
            + 12
        )
        color = COLORS[
            event_index
            % len(
                COLORS
            )
        ]
        parts += [
            f'<line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" y2="{y_line:.1f}" stroke="{color}" stroke-width="2"/>',
            f'<circle cx="{x:.1f}" cy="{axis_y}" r="5" fill="{color}"/>',
            f'<text x="{x:.1f}" y="{y}" text-anchor="middle" font-size="13" font-weight="bold">{label}</text>',
            f'<text x="{x:.1f}" y="{y+17}" text-anchor="middle" font-size="11">{detail}</text>',
        ]

    parts += [
        '<text x="475" y="417" text-anchor="middle" font-size="11">Dates are approximate constraints, not a complete demographic reconstruction. Archaeological BP conventions and calendar-year simplifications are not treated as exact equivalents.</text>',
        "</svg>",
    ]
    path.write_text(
        "\n".join(
            parts
        )
    )


def regional_trajectory_svg(
    path: Path,
) -> None:
    scenario = (
        make_debate_historical_scenario()
    )
    result = (
        deterministic_historical_genealogy(
            scenario
        )
    )
    width, height = (
        950,
        540,
    )
    left, top, plot_w, plot_h = (
        85,
        60,
        790,
        390,
    )
    gmax = (
        scenario.generations
    )

    def px(g):
        return (
            left
            + plot_w
            * g
            / gmax
        )

    def py(v):
        return (
            top
            + plot_h
            * (
                1
                - v
            )
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:2.6}</style>',
        '<text x="475" y="30" text-anchor="middle" font-size="22">Two-founder genealogical spread under the default constraint scenario</text>',
    ]

    for k in range(
        6
    ):
        v = (
            k
            / 5
        )
        y = py(
            v
        )
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>',
        ]

    keep = sorted(
        set(
            range(
                0,
                432,
                10,
            )
        )
        | set(
            range(
                431,
                441,
            )
        )
    )

    for idx, name in enumerate(
        scenario.region_names
    ):
        vals = (
            result.all_founders_fraction_by_region[
                :,
                idx,
            ]
        )
        points = " ".join(
            f"{px(int(result.generations[k])):.1f},{py(float(vals[k])):.1f}"
            for k in keep
        )
        parts.append(
            f'<polyline class="line" stroke="{COLORS[idx]}" points="{points}"/>'
        )
        yleg = (
            80
            + 20
            * idx
        )
        parts += [
            f'<line x1="615" y1="{yleg}" x2="647" y2="{yleg}" stroke="{COLORS[idx]}" stroke-width="3"/>',
            f'<text x="657" y="{yleg+5}" font-size="11">{name}</text>',
        ]

    late = (
        scenario.metadata[
            "late_contact_start_generation"
        ]
    )
    xlate = px(
        late
    )
    parts += [
        f'<line x1="{xlate:.1f}" y1="{top}" x2="{xlate:.1f}" y2="{top+plot_h}" stroke="#555" stroke-dasharray="6 5"/>',
        f'<text x="{xlate-5:.1f}" y="{top+plot_h-10}" text-anchor="end" font-size="11">late contact window begins</text>',
    ]

    for g in [
        0,
        100,
        200,
        300,
        400,
        440,
    ]:
        x = px(
            g
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top+plot_h+24}" text-anchor="middle" font-size="12">{g}</text>'
        )

    parts += [
        '<text x="480" y="493" text-anchor="middle" font-size="15">Generations after founder insertion</text>',
        '<text x="24" y="255" transform="rotate(-90 24 255)" text-anchor="middle" font-size="15">Fraction descended from both founders</text>',
        '<text x="475" y="522" text-anchor="middle" font-size="11">Default cross-region rates are sensitivity parameters, not empirical Holocene migration estimates.</text>',
        "</svg>",
    ]
    path.write_text(
        "\n".join(
            parts
        )
    )


def late_contact_svg(
    path: Path,
) -> None:
    rates = np.array(
        [
            0,
            0.0001,
            0.00025,
            0.0005,
            0.001,
            0.002,
            0.003,
            0.005,
            0.0075,
            0.01,
            0.015,
            0.02,
        ]
    )
    summary = (
        simulate_late_contact_sensitivity(
            rates,
            generations=9,
            population_size=100,
            replicates=5_000,
            seed=20260920,
        )
    )

    width, height = (
        950,
        540,
    )
    left, top, plot_w, plot_h = (
        85,
        65,
        790,
        370,
    )
    xmax = 0.02

    def px(x):
        return (
            left
            + plot_w
            * x
            / xmax
        )

    def py(v):
        return (
            top
            + plot_h
            * (
                1
                - v
            )
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}.line{fill:none;stroke-width:3}</style>',
        '<text x="475" y="30" text-anchor="middle" font-size="22">Late-contact sensitivity after a long hard isolation</text>',
    ]

    for k in range(
        6
    ):
        v = (
            k
            / 5
        )
        y = py(
            v
        )
        parts += [
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}"/>',
            f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>',
        ]

    for x in [
        0,
        0.002,
        0.005,
        0.01,
        0.015,
        0.02,
    ]:
        xp = px(
            x
        )
        parts.append(
            f'<text x="{xp:.1f}" y="{top+plot_h+24}" text-anchor="middle" font-size="12">{100*x:g}%</text>'
        )

    series = [
        (
            summary.mean_final_fraction,
            COLORS[0],
            "mean final descendant fraction",
        ),
        (
            summary.fixation_probability,
            COLORS[1],
            "probability of complete fixation",
        ),
    ]

    for idx, (
        values,
        color,
        label,
    ) in enumerate(
        series
    ):
        points = " ".join(
            f"{px(float(x)):.1f},{py(float(v)):.1f}"
            for x, v in zip(
                rates,
                values,
            )
        )
        parts.append(
            f'<polyline class="line" stroke="{color}" points="{points}"/>'
        )
        for x, v in zip(
            rates,
            values,
        ):
            parts.append(
                f'<circle cx="{px(float(x)):.1f}" cy="{py(float(v)):.1f}" r="3.5" fill="{color}"/>'
            )

        yleg = (
            82
            + idx
            * 24
        )
        parts += [
            f'<line x1="560" y1="{yleg}" x2="595" y2="{yleg}" stroke="{color}" stroke-width="3"/>',
            f'<text x="605" y="{yleg+5}" font-size="12">{label}</text>',
        ]

    parts += [
        '<text x="480" y="488" text-anchor="middle" font-size="15">External-parent probability per parental draw</text>',
        '<text x="24" y="250" transform="rotate(-90 24 250)" text-anchor="middle" font-size="15">Final fraction / fixation probability</text>',
        '<text x="475" y="518" text-anchor="middle" font-size="11">Best-case conditional test: external pool already 100% descended from the founders; 9 generations, N=100, 5,000 replicates.</text>',
        "</svg>",
    ]
    path.write_text(
        "\n".join(
            parts
        )
    )


def contact_animation_svg(
    path: Path,
) -> None:
    rates = [
        0.001,
        0.005,
        0.01,
        0.02,
    ]
    labels = [
        "0.1%",
        "0.5%",
        "1%",
        "2%",
    ]
    histories = []

    for rate in rates:
        values = [
            0.0
        ]
        f = 0.0
        for _ in range(
            9
        ):
            f = (
                1
                - (
                    (
                        1
                        - rate
                    )
                    * (
                        1
                        - f
                    )
                )
                ** 2
            )
            values.append(
                f
            )
        histories.append(
            values
        )

    width, height = (
        900,
        430,
    )
    baseline = 335
    top = 75
    max_h = (
        baseline
        - top
    )
    xs = [
        120,
        315,
        510,
        705,
    ]
    bar_w = 105
    duration = 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.grid{stroke:#ddd}</style>',
        '<text x="450" y="30" text-anchor="middle" font-size="22">Best-case ancestry spread during a 9-generation late-contact window</text>',
    ]

    for k in range(
        6
    ):
        v = (
            k
            / 5
        )
        y = (
            baseline
            - max_h
            * v
        )
        parts += [
            f'<line class="grid" x1="75" y1="{y:.1f}" x2="840" y2="{y:.1f}"/>',
            f'<text x="63" y="{y+5:.1f}" text-anchor="end" font-size="12">{v:.1f}</text>',
        ]

    for i, (
        label,
        values,
    ) in enumerate(
        zip(
            labels,
            histories,
        )
    ):
        heights = [
            max_h
            * value
            for value in values
        ]
        ys = [
            baseline
            - height_value
            for height_value
            in heights
        ]
        y_values = ";".join(
            f"{value:.2f}"
            for value in ys
        )
        height_values = ";".join(
            f"{value:.2f}"
            for value in heights
        )
        parts += [
            f'<rect x="{xs[i]}" y="{ys[0]:.2f}" width="{bar_w}" height="{heights[0]:.2f}" fill="{COLORS[i]}">',
            f'<animate attributeName="y" values="{y_values}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            f'<animate attributeName="height" values="{height_values}" dur="{duration}s" repeatCount="indefinite" calcMode="discrete"/>',
            "</rect>",
            f'<text x="{xs[i]+bar_w/2}" y="365" text-anchor="middle" font-size="13">{label} external parents</text>',
        ]

    parts += [
        '<text x="450" y="398" text-anchor="middle" font-size="11">Deterministic expectation, starting from zero founder ancestry inside the isolated deme; external pool assumed universal.</text>',
        "</svg>",
    ]
    path.write_text(
        "\n".join(
            parts
        )
    )


def main() -> None:
    timeline_svg(
        OUT
        / "model09_historical_timeline.svg"
    )
    regional_trajectory_svg(
        OUT
        / "model09_regional_trajectory.svg"
    )
    late_contact_svg(
        OUT
        / "model09_late_contact_sensitivity.svg"
    )
    contact_animation_svg(
        OUT
        / "model09_late_contact_animation.svg"
    )


if __name__ == "__main__":
    main()
