"""Model 15: descriptive evolution of cooperation, punishment, and conformity.

The model is intentionally descriptive. It can show how cooperative or harmful
norms spread under payoff and conformity pressures. It cannot infer that a
behavior is morally right because it is common, stable, or fitness-enhancing.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class NormDynamicsResult:
    time: np.ndarray
    cooperative_fraction: np.ndarray
    cooperation_cost: float
    punishment_strength: float
    conformity_strength: float
    learning_rate: float


def selection_gradient(
    cooperative_fraction: float,
    cooperation_cost: float = 0.2,
    punishment_strength: float = 0.0,
    conformity_strength: float = 0.0,
) -> float:
    """Frequency-dependent advantage of cooperation.

    Defectors pay an expected social penalty proportional to the fraction of
    cooperators/punishers. Conformity favors whichever behavior is already more
    common. This is a pedagogical cultural-evolution model, not a fit to one
    historical society.
    """
    x = float(cooperative_fraction)
    if not 0.0 <= x <= 1.0:
        raise ValueError("cooperative_fraction must lie in [0, 1]")
    if cooperation_cost < 0.0:
        raise ValueError("cooperation_cost must be non-negative")
    if punishment_strength < 0.0:
        raise ValueError("punishment_strength must be non-negative")
    if conformity_strength < 0.0:
        raise ValueError("conformity_strength must be non-negative")

    payoff_component = punishment_strength * x - cooperation_cost
    conformity_component = conformity_strength * (2.0 * x - 1.0)
    return float(payoff_component + conformity_component)


def simulate_norm_dynamics(
    initial_cooperation: float = 0.5,
    steps: int = 300,
    dt: float = 0.05,
    cooperation_cost: float = 0.2,
    punishment_strength: float = 0.0,
    conformity_strength: float = 0.0,
    learning_rate: float = 1.0,
) -> NormDynamicsResult:
    """Euler integration of a replicator-like cultural dynamic."""
    if not 0.0 <= initial_cooperation <= 1.0:
        raise ValueError("initial_cooperation must lie in [0, 1]")
    if steps < 1 or dt <= 0.0 or learning_rate < 0.0:
        raise ValueError("invalid integration settings")

    x = np.empty(steps + 1, dtype=float)
    x[0] = initial_cooperation
    for t in range(steps):
        g = selection_gradient(
            x[t],
            cooperation_cost=cooperation_cost,
            punishment_strength=punishment_strength,
            conformity_strength=conformity_strength,
        )
        dx = learning_rate * x[t] * (1.0 - x[t]) * g
        x[t + 1] = np.clip(x[t] + dt * dx, 0.0, 1.0)

    return NormDynamicsResult(
        time=np.arange(steps + 1, dtype=float) * dt,
        cooperative_fraction=x,
        cooperation_cost=float(cooperation_cost),
        punishment_strength=float(punishment_strength),
        conformity_strength=float(conformity_strength),
        learning_rate=float(learning_rate),
    )


def simulate_conformity_only(
    initial_norm_fraction: float,
    steps: int = 300,
    dt: float = 0.05,
    conformity_strength: float = 1.0,
) -> np.ndarray:
    """Content-neutral majority copying.

    The state can represent a cooperative, neutral, or harmful norm. The
    dynamics do not know its moral content.
    """
    if not 0.0 <= initial_norm_fraction <= 1.0:
        raise ValueError("initial_norm_fraction must lie in [0, 1]")
    if conformity_strength < 0.0:
        raise ValueError("conformity_strength must be non-negative")
    if steps < 1 or dt <= 0:
        raise ValueError("invalid integration settings")

    x = np.empty(steps + 1, dtype=float)
    x[0] = initial_norm_fraction
    for t in range(steps):
        pressure = conformity_strength * (2.0 * x[t] - 1.0)
        x[t + 1] = np.clip(
            x[t] + dt * x[t] * (1.0 - x[t]) * pressure,
            0.0,
            1.0,
        )
    return x


def final_cooperation_grid(
    initial_values: np.ndarray,
    punishment_values: np.ndarray,
    conformity_strength: float,
    cooperation_cost: float = 0.2,
    steps: int = 500,
    dt: float = 0.05,
) -> np.ndarray:
    """Grid of final cooperation fractions for sensitivity analysis."""
    initials = np.asarray(initial_values, dtype=float)
    punishments = np.asarray(punishment_values, dtype=float)
    out = np.empty((initials.size, punishments.size), dtype=float)
    for i, x0 in enumerate(initials):
        for j, p in enumerate(punishments):
            out[i, j] = simulate_norm_dynamics(
                initial_cooperation=float(x0),
                steps=steps,
                dt=dt,
                cooperation_cost=cooperation_cost,
                punishment_strength=float(p),
                conformity_strength=conformity_strength,
            ).cooperative_fraction[-1]
    return out
