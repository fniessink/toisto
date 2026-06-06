# /// script
# requires-python = ">=3.13"
# dependencies = ["matplotlib"]
# ///
"""Generate the growth-factor graph used in the "Spaced repetition" section of software.md.

Regenerate the PNG with: uv run --no-project --script docs/plot_growth_factor.py
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt

B = 5.0  # Mirrors SKIP_INTERVAL_MAX_GROWTH_FACTOR in src/toisto/model/quiz/retention.py
TAU = 1.0  # Mirrors SKIP_INTERVAL_DAMPING_TIMESCALE (one day), expressed in days


def growth_factor(retention_period_days: float) -> float:
    """Return the damped growth factor for a retention period given in days."""
    return B / math.log(math.e + retention_period_days / TAU)


def main() -> None:
    """Plot the growth factor and the effective per-review interval multiplier, and save the figure."""
    # Retention period from ~1.4 minutes to 1000 days, log-spaced.
    xs = [10 ** (-3 + 6 * i / 600) for i in range(601)]
    factor = [growth_factor(x) for x in xs]
    multiplier = [1 + f for f in factor]

    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))

    left.semilogx(xs, factor, color="#1f77b4", lw=2)
    left.set_title("Damped growth factor")
    left.set_xlabel("retention period R (days, log scale)")
    left.set_ylabel("growth factor  B / ln(e + R/tau)")
    left.set_ylim(0, B + 0.5)
    left.grid(visible=True, which="both", alpha=0.3)

    right.semilogx(xs, multiplier, color="#1f77b4", lw=2, label="effective multiplier = 1 + growth_factor")
    right.axhline(5, color="#2ca02c", ls=":", lw=1.2, label="Pimsleur graduated schedule: ~x5")
    right.axhline(2.5, color="#9467bd", ls=":", lw=1.2, label="SuperMemo SM-2: ~x2.5")
    for retention_period in (1, 10, 60, 300):
        m = 1 + growth_factor(retention_period)
        right.plot(retention_period, m, "o", color="#1f77b4")
        right.annotate(f"{retention_period}d: x{m:.1f}", (retention_period, m),
                       textcoords="offset points", xytext=(6, 8), fontsize=9)
    right.set_title("Effective per-review interval multiplier")
    right.set_xlabel("retention period R (days, log scale)")
    right.set_ylabel("interval multiplier (1 + growth_factor)")
    right.set_ylim(0, B + 1.5)
    right.grid(visible=True, which="both", alpha=0.3)
    right.legend(loc="upper right", fontsize=9)

    fig.suptitle("Toisto growth factor (B=5, tau=1 day): short intervals expand fast, long intervals expand gently",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    output = Path(__file__).with_name("growth_factor.png")
    fig.savefig(output, dpi=130)
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
