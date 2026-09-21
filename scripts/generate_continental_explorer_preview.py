"""Generate the static README preview for the continental explorer."""

from pathlib import Path
import json

import numpy as np

from evolution_creation.continental_explorer import (
    diagnose_scenario,
    parent_source_matrix_from_offdiag,
    simulate_continental_explorer,
)

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

data = json.loads(
    Path("data/continental_explorer_defaults.json").read_text()
)
regions = data["regions"]
initial = [
    data["population_preset_9000_bce"]["values"][name]
    for name in regions
]
target = [
    data["population_target_2000_ce"]["values"][name]
    for name in regions
]
matrix = parent_source_matrix_from_offdiag(
    data["parent_source_offdiag_default"]["values"]
)
tasmania_pair = (
    regions.index("Australia/Oceania"),
    regions.index("Tasmania"),
)

result = simulate_continental_explorer(
    initial_population=initial,
    target_population=target,
    parent_source_matrix=matrix,
    mixing_strength=data["mixing_strength_default"]["values"],
    founder_age_years=11_000,
    generation_interval_years=28,
    founder_region=regions.index("Middle East"),
    founder_pair_joint_children=2,
    late_contact_age_years=data["late_contact_default"]["start_years_ago"],
    late_contact_multiplier=data["late_contact_default"]["external_parent_multiplier"],
    barrier_pairs=[tasmania_pair],
    barrier_release_age_years=data["tasmania_barrier_default"]["release_years_ago"],
    region_names=regions,
)

diagnosis = diagnose_scenario(result)
final_both = result.both_founders_fraction[-1]
global_both = result.global_both_founders_fraction[-1]
global_dna = result.global_genetic_ancestry[-1]

coords = {
    "Middle East": (452, 395),
    "Africa": (306, 452),
    "Europe": (407, 346),
    "Asia": (585, 376),
    "Americas": (177, 370),
    "Australia/Oceania": (700, 518),
    "Tasmania": (730, 585),
}
colors = {
    "Middle East": "#7b2cbf",
    "Africa": "#2a9d8f",
    "Europe": "#457b9d",
    "Asia": "#f4a261",
    "Americas": "#e76f51",
    "Australia/Oceania": "#264653",
    "Tasmania": "#d1495b",
}

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760">',
    '<rect width="100%" height="100%" fill="#f7fafc"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#172033}.card{fill:white;stroke:#dbe5ec}.muted{fill:#667085}.edge{stroke:#90a4b4;stroke-width:2;opacity:.5}.barrier{stroke:#d00000;stroke-width:4;stroke-dasharray:8 6}</style>',
    '<text x="48" y="52" font-size="27" font-weight="700">Continental founder-spread explorer</text>',
    '<text x="48" y="78" font-size="14" class="muted">Seven regions • deterministic + Monte Carlo • hard Tasmania barrier • A/B scenario comparison</text>',
    '<rect class="card" x="48" y="104" width="250" height="98" rx="16"/>',
    '<rect class="card" x="314" y="104" width="250" height="98" rx="16"/>',
    '<rect class="card" x="580" y="104" width="250" height="98" rx="16"/>',
    '<rect class="card" x="846" y="104" width="386" height="98" rx="16"/>',
    '<text x="68" y="132" font-size="12" class="muted">Present global both-founder genealogy</text>',
    f'<text x="68" y="174" font-size="27" font-weight="700">{100*global_both:.4f}%</text>',
    '<text x="334" y="132" font-size="12" class="muted">Present mean founder-pair DNA</text>',
    f'<text x="334" y="174" font-size="27" font-weight="700">{100*global_dna:.6f}%</text>',
    '<text x="600" y="132" font-size="12" class="muted">Present limiting region</text>',
    f'<text x="600" y="174" font-size="27" font-weight="700">{diagnosis.limiting_region}</text>',
    '<text x="866" y="132" font-size="12" class="muted">Default Tasmania outcome</text>',
    f'<text x="866" y="169" font-size="24" font-weight="700">{100*final_both[-1]:.1f}% descended from both founders</text>',
    '<text x="866" y="190" font-size="12" class="muted">Teaching defaults; not a historical estimate</text>',
    '<rect class="card" x="48" y="226" width="760" height="460" rx="18"/>',
    '<text x="76" y="260" font-size="17" font-weight="700">Regional spread at the present</text>',
    '<text x="76" y="282" font-size="12" class="muted">Node fill labels show both-founder genealogy; edge width is schematic</text>',
]

edges = [
    ("Middle East", "Africa"),
    ("Middle East", "Europe"),
    ("Middle East", "Asia"),
    ("Asia", "Americas"),
    ("Asia", "Australia/Oceania"),
]
for a, b in edges:
    xa, ya = coords[a]
    xb, yb = coords[b]
    parts.append(
        f'<line class="edge" x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}"/>'
    )
xa, ya = coords["Australia/Oceania"]
xb, yb = coords["Tasmania"]
parts.append(
    f'<line class="barrier" x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}"/>'
)

for i, name in enumerate(regions):
    x, y = coords[name]
    radius = 23 if name == "Tasmania" else 30
    parts += [
        f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{colors[name]}" stroke="white" stroke-width="3"/>',
        f'<text x="{x}" y="{y+4}" text-anchor="middle" fill="white" font-size="10" font-weight="700">{100*final_both[i]:.1f}%</text>',
        f'<text x="{x}" y="{y+radius+18}" text-anchor="middle" font-size="12" font-weight="600">{name}</text>',
    ]

parts += [
    '<text x="606" y="612" fill="#d00000" font-size="11" font-weight="700">hard barrier until recent contact</text>',
    '<rect class="card" x="832" y="226" width="400" height="218" rx="18"/>',
    '<text x="860" y="260" font-size="17" font-weight="700">Monte Carlo mode</text>',
    '<text x="860" y="286" font-size="12" class="muted">Adds finite-population lineage loss and 5–95% bands</text>',
    '<path d="M870 350 C920 344 957 331 1001 311 C1048 291 1105 278 1190 271 L1190 327 C1110 330 1054 337 1001 349 C950 360 912 365 870 366 Z" fill="#2d7dd2" opacity=".16"/>',
    '<path d="M870 360 C920 352 960 339 1002 322 C1050 303 1107 294 1190 288" fill="none" stroke="#2d7dd2" stroke-width="3"/>',
    '<text x="860" y="414" font-size="12">Reports P(all regions ≥50%, ≥90%, ≥99%) and lineage-extinction probability.</text>',
    '<rect class="card" x="832" y="462" width="400" height="224" rx="18"/>',
    '<text x="860" y="496" font-size="17" font-weight="700">A/B scenario comparison</text>',
    '<text x="860" y="520" font-size="12" class="muted">Recent contact versus permanent Tasmania isolation</text>',
    '<text x="860" y="558" font-size="13" font-weight="600">Tasmania present both-founder fraction</text>',
    '<rect x="860" y="576" width="286" height="25" rx="8" fill="#edf1f5"/>',
    f'<rect x="860" y="576" width="{286*final_both[-1]:.1f}" height="25" rx="8" fill="#d1495b"/>',
    f'<text x="1157" y="594" font-size="12">{100*final_both[-1]:.1f}%</text>',
    '<text x="860" y="630" font-size="13" font-weight="600">Permanent hard barrier</text>',
    '<rect x="860" y="646" width="286" height="25" rx="8" fill="#edf1f5"/>',
    '<rect x="860" y="646" width="2" height="25" rx="8" fill="#d00000"/>',
    '<text x="1157" y="664" font-size="12">0%</text>',
    '<text x="48" y="725" font-size="12" class="muted">Teaching defaults. Migration/mixing rates and Tasmania start population are sensitivity assumptions, not reconstructed historical measurements.</text>',
    '</svg>',
]

(OUT / "continental_explorer_preview.svg").write_text(
    "\n".join(parts)
)
