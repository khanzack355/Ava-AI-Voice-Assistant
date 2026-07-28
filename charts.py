"""
charts.py

Turns a small dict of financial metrics (income, expenses, savings) into a
simple, clean bar chart PNG that can be shown on screen and embedded into
the PDF and Word reports. Kept deliberately simple: one chart type, no
external chart library dependency beyond matplotlib, and it degrades
gracefully (returns None) if there isn't enough data to chart honestly.
"""

import io

import matplotlib
matplotlib.use("Agg")  # headless rendering, no display needed
import matplotlib.pyplot as plt

BAR_COLORS = {
    "Income": "#3F6B52",
    "Expenses": "#B0463B",
    "Savings": "#3B5B7A",
}


def build_financial_bar_chart(metrics: dict) -> bytes | None:
    """
    metrics: {"income": float|None, "expenses": float|None,
              "savings": float|None, "currency_symbol": str}
    Returns PNG bytes, or None if there isn't enough data to chart.
    """
    labels, values, colors = [], [], []
    for key, display in (("income", "Income"), ("expenses", "Expenses"), ("savings", "Savings")):
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            labels.append(display)
            values.append(value)
            colors.append(BAR_COLORS[display])

    if len(values) < 2:
        return None

    symbol = metrics.get("currency_symbol") or ""

    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=160)
    bars = ax.bar(labels, values, color=colors, width=0.55)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{symbol}{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#1C2B33",
        )

    ax.set_title("Approximate Monthly Financial Snapshot", fontsize=11, color="#1C2B33", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.tick_params(axis="x", labelsize=10, colors="#1C2B33")
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True)
    plt.close(fig)
    buffer.seek(0)
    return buffer.read()
