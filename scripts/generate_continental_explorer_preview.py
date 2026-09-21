"""Generate a static SVG preview for the continental explorer."""

from pathlib import Path

import json
import numpy as np

from evolution_creation.continental_explorer import (
    parent_source_matrix_from_offdiag,
    simulate_continental_explorer,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

data = json.loads(
    Path(
        "data/continental_explorer_defaults.json"
    ).read_text()
)
regions = data["regions"]
initial = [
    data[
        "population_preset_9000_bce"
    ][
        "values"
    ][
        name
    ]
    for name in regions
]
target = [
    data[
        "population_target_2000_ce"
    ][
        "values"
    ][
        name
    ]
    for name in regions
]
matrix = parent_source_matrix_from_offdiag(
    data[
        "parent_source_offdiag_default"
    ][
        "values"
    ]
)
result = simulate_continental_explorer(
    initial_population=initial,
    target_population=target,
    parent_source_matrix=matrix,
    mixing_strength=data[
        "mixing_strength_default"
    ][
        "values"
    ],
    founder_age_years=11_000,
    generation_interval_years=28,
    founder_region=0,
    founder_pair_joint_children=2,
    late_contact_age_years=500,
    late_contact_multiplier=4,
)

coords = {
    "Middle East": (455, 180),
    "Africa": (410, 250),
    "Europe": (410, 125),
    "Asia": (590, 150),
    "Americas": (185, 190),
    "Oceania": (665, 285),
}

snapshots = [
    0,
    len(
        result.generations
    )
    // 2,
    len(
        result.generations
    )
    - 1,
]
panel_x = [
    0,
    330,
    660,
]

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="990" height="430" viewBox="0 0 990 430">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#111}.panel{fill:#f7f7f7;stroke:#ddd}.edge{stroke:#bbb;stroke-width:1.2}.node{stroke:#333;stroke-width:1}</style>',
    '<text x="495" y="28" text-anchor="middle" font-size="22">Interactive continental founder-spread explorer</text>',
]

for panel, generation in enumerate(
    snapshots
):
    x0 = panel_x[
        panel
    ]
    parts.append(
        f'<rect class="panel" x="{x0+8}" y="45" width="314" height="330" rx="12"/>'
    )
    years = int(
        round(
            result.years_before_present[
                generation
            ]
        )
    )
    label = (
        "present"
        if years == 0
        else f"{years:,} years ago"
    )
    parts.append(
        f'<text x="{x0+165}" y="72" text-anchor="middle" font-size="15" font-weight="bold">{label}</text>'
    )

    scaled = {
        name: (
            x0
            + 20
            + (
                x
                - 150
            )
            * 0.42,
            80
            + (
                y
                - 100
            )
            * 0.72,
        )
        for name, (
            x,
            y,
        )
        in coords.items()
    }

    edges = [
        (
            "Middle East",
            "Africa",
        ),
        (
            "Middle East",
            "Europe",
        ),
        (
            "Middle East",
            "Asia",
        ),
        (
            "Asia",
            "Americas",
        ),
        (
            "Asia",
            "Oceania",
        ),
    ]
    for a, b in edges:
        xa, ya = scaled[
            a
        ]
        xb, yb = scaled[
            b
        ]
        parts.append(
            f'<line class="edge" x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}"/>'
        )

    for region_index, name in enumerate(
        regions
    ):
        x, y = scaled[
            name
        ]
        value = float(
            result.both_founders_fraction[
                generation,
                region_index,
            ]
        )
        pop = float(
            result.populations[
                generation,
                region_index,
            ]
        )
        radius = (
            8.0
            + 4.0
            * np.log10(
                max(
                    pop,
                    10.0,
                )
            )
        )
        opacity = (
            0.12
            + 0.88
            * value
        )
        parts.append(
            f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="#d62728" fill-opacity="{opacity:.3f}"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y+radius+13:.1f}" text-anchor="middle" font-size="10">{name}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-size="9">{100*value:.1f}%</text>'
        )

parts += [
    '<text x="495" y="400" text-anchor="middle" font-size="12">Circle size = modeled population; red intensity and label = fraction descended from both founders.</text>',
    '<text x="495" y="420" text-anchor="middle" font-size="10">Preview uses editable teaching defaults. Migration and mixing presets are not empirical Holocene estimates.</text>',
    '</svg>',
]

(
    OUT
    / "continental_explorer_preview.svg"
).write_text(
    "\n".join(
        parts
    )
)
