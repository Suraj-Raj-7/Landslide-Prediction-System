"""Phase C, step 12: one summary chart of all models compared so far.

PURPOSE
  Two scores per method, both for HP rows, all from year-blocked
  out-of-fold predictions (data/phaseC/two_part_comparison.csv):
    WHEN  (timing): recorded slides vs safe days at the same places;
    WHERE + WHEN (full): recorded slides vs all negatives.
  A rain-only rule is included as the baseline.

INPUTS   data/phaseC/two_part_comparison.csv
OUTPUTS  docs/figures/model_comparison.png
RUN      .venv/Scripts/python -W ignore src/phaseC_12_summary_figure.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHOW = {"Rain on the day alone": "Rain on the day\n(baseline)",
        "Single model, full 38, real roads": "Single model\nfull data",
        "Single model, live 28, real roads": "Single model\nlive data",
        "Single model, live 28, road-neutral": "Single model\nlive, road-neutral",
        "Two-part live, when=LR, real roads": "Two-part\nlive data",
        "Two-part live, when=LR, road-neutral": "Two-part\nlive, road-neutral"}


def main():
    r = pd.read_csv("data/phaseC/two_part_comparison.csv").set_index("method").loc[list(SHOW)]
    x = np.arange(len(r))
    fig, ax = plt.subplots(figsize=(11, 4.6))
    b1 = ax.bar(x - 0.2, r.timing_auc_HP, 0.4, label="WHEN: slide day vs safe day, same place", color="#457b9d")
    b2 = ax.bar(x + 0.2, r.full_auc_HP, 0.4, label="WHERE + WHEN: slides vs all negatives", color="#e76f51")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.005, f"{b.get_height():.2f}",
                    ha="center", fontsize=8)
    ax.axhline(0.5, color="grey", lw=0.8, ls=":")
    ax.set_xticks(x, [SHOW[m] for m in r.index], fontsize=8.5)
    ax.set_ylim(0.45, 0.9)
    ax.set_ylabel("ROC AUC, HP (whole years held out)")
    ax.set_title("Model comparison, Himachal Pradesh rows (0.5 = coin toss)")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig("docs/figures/model_comparison.png", dpi=170)
    print(r[["timing_auc_HP", "full_auc_HP"]].to_string())


if __name__ == "__main__":
    main()
