#!/usr/bin/env python3
"""Generate charts for analytical report PDF."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use("Agg")
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

BASE = Path(__file__).parent
FIG = BASE / "figures"
FIG.mkdir(exist_ok=True)

with open(BASE / "data.json", encoding="utf-8") as f:
    D = json.load(f)

LEVELS = D["levels"]
SCALES = D["scales"]
SHORT = [
    "Семья", "Отечество", "Природа", "Мир", "Труд", "Культура",
    "Знания", "Человек", "Другой", "Иной", "Телесное Я",
    "Душевное Я", "Духовное Я",
]
COLORS = ["#10b981", "#34d399", "#fbbf24", "#ef4444"]
CLASSES = [c for c in D["classes"] if c != "Все"]


def positivity(sd):
    total = sum(sd.values())
    if not total:
        return 0.0
    score = (
        sd.get("устойчиво-позитивное", 0) * 3
        + sd.get("ситуативно-позитивное", 0) * 2
        + sd.get("ситуативно-негативное", 0) * 1
    )
    return score / (total * 3) * 100


def pos_pct(sd):
    total = sum(sd.values())
    if not total:
        return 0.0
    return (
        sd.get("устойчиво-позитивное", 0) + sd.get("ситуативно-позитивное", 0)
    ) / total * 100


def class_n(cls):
    return sum(D["data"][cls][SCALES[0]].values())


# --- 1. Radar: school overall ---
all_data = D["data"]["Все"]
vals = [positivity(all_data[s]) for s in SCALES]
angles = np.linspace(0, 2 * np.pi, len(SCALES), endpoint=False).tolist()
vals_c = vals + [vals[0]]
angles_c = angles + [angles[0]]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax.plot(angles_c, vals_c, "o-", color="#4f46e5", linewidth=2)
ax.fill(angles_c, vals_c, alpha=0.25, color="#4f46e5")
ax.set_xticks(angles)
ax.set_xticklabels(SHORT, size=9)
ax.set_ylim(0, 100)
ax.set_title("Общий профиль школы (индекс позитивности, %)", pad=20, size=12)
fig.tight_layout()
fig.savefig(FIG / "radar_school.png", dpi=150, bbox_inches="tight")
plt.close()

# --- 2. Strong / weak scales (school) ---
pairs = [(SHORT[i], positivity(all_data[SCALES[i]])) for i in range(len(SCALES))]
pairs.sort(key=lambda x: x[1])
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
low = pairs[:4]
high = pairs[-4:][::-1]
axes[0].barh([p[0] for p in low], [p[1] for p in low], color="#ef4444")
axes[0].set_xlim(0, 100)
axes[0].set_title("Зоны риска (низкий индекс)")
axes[0].set_xlabel("%")
for i, (n, v) in enumerate(low):
    axes[0].text(v + 1, i, f"{v:.0f}%", va="center", size=9)
axes[1].barh([p[0] for p in high], [p[1] for p in high], color="#10b981")
axes[1].set_xlim(0, 100)
axes[1].set_title("Сильные стороны (высокий индекс)")
axes[1].set_xlabel("%")
for i, (n, v) in enumerate(high):
    axes[1].text(v + 1, i, f"{v:.0f}%", va="center", size=9)
fig.suptitle("Сравнение шкал: обобщённо по школе (n=129)", size=12)
fig.tight_layout()
fig.savefig(FIG / "strengths_risks.png", dpi=150, bbox_inches="tight")
plt.close()

# --- 3. Heatmap: classes x scales ---
matrix = []
for cls in CLASSES:
    row = [positivity(D["data"][cls][s]) for s in SCALES]
    matrix.append(row)
matrix = np.array(matrix)

fig, ax = plt.subplots(figsize=(14, 5))
im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=30, vmax=95)
ax.set_xticks(range(len(SHORT)))
ax.set_xticklabels(SHORT, rotation=45, ha="right", size=8)
ax.set_yticks(range(len(CLASSES)))
labels_y = [f"{c} (n={class_n(c)})" for c in CLASSES]
ax.set_yticklabels(labels_y)
for i in range(len(CLASSES)):
    for j in range(len(SCALES)):
        ax.text(j, i, f"{matrix[i, j]:.0f}", ha="center", va="center", size=7,
                color="black" if 45 < matrix[i, j] < 80 else "white")
ax.set_title("Индекс позитивности по классам и шкалам (%)", pad=12)
fig.colorbar(im, ax=ax, label="%")
fig.tight_layout()
fig.savefig(FIG / "heatmap_classes.png", dpi=150, bbox_inches="tight")
plt.close()

# --- 4. Problem scales by class ---
risk_idx = [5, 11, 3]  # culture, soul, world
risk_names = ["Культура", "Душевное Я", "Мир"]
x = np.arange(len(CLASSES))
w = 0.25
fig, ax = plt.subplots(figsize=(11, 5))
for k, (ri, name) in enumerate(zip(risk_idx, risk_names)):
    vals_c = [pos_pct(D["data"][cls][SCALES[ri]]) for cls in CLASSES]
    ax.bar(x + (k - 1) * w, vals_c, width=w, label=name)
ax.set_xticks(x)
ax.set_xticklabels([f"{c}\n(n={class_n(c)})" for c in CLASSES])
ax.set_ylabel("Доля позитивных ответов, %")
ax.set_ylim(0, 100)
ax.legend()
ax.set_title("Проблемные сферы: сравнение классов")
ax.axhline(50, color="gray", ls="--", alpha=0.5)
fig.tight_layout()
fig.savefig(FIG / "classes_risk.png", dpi=150, bbox_inches="tight")
plt.close()

# --- 5. Stacked bar: UP/SP/SN/UN for soul & culture (school) ---
def stacked_bar(scale_idx, title, fname):
    sd = all_data[SCALES[scale_idx]]
    counts = [sd.get(l, 0) for l in LEVELS]
    total = sum(counts) or 1
    pcts = [c / total * 100 for c in counts]
    fig, ax = plt.subplots(figsize=(6, 4))
    left = 0
    for pct, col, lab in zip(pcts, COLORS, ["УП", "СП", "СН", "УН"]):
        ax.barh(0, pct, left=left, color=col, label=lab, height=0.5)
        if pct > 5:
            ax.text(left + pct / 2, 0, f"{pct:.0f}%", ha="center", va="center", size=10)
        left += pct
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("%")
    ax.set_title(title)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4)
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=150, bbox_inches="tight")
    plt.close()

stacked_bar(11, "Душевное «Я» — структура ответов (вся школа)", "stack_soul.png")
stacked_bar(5, "Культура — структура ответов (вся школа)", "stack_culture.png")

# --- 6. Class comparison: overall index (avg of 13 scales) ---
avg_by_class = []
for cls in CLASSES:
    m = np.mean([positivity(D["data"][cls][s]) for s in SCALES])
    avg_by_class.append(m)
school_avg = np.mean([positivity(all_data[s]) for s in SCALES])

order = np.argsort(avg_by_class)[::-1]
fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(
    [CLASSES[i] for i in order],
    [avg_by_class[i] for i in order],
    color="#6366f1",
)
ax.axhline(school_avg, color="#dc2626", ls="--", lw=2, label=f"Среднее по школе ({school_avg:.0f}%)")
ax.set_ylabel("Средний индекс по 13 шкалам, %")
ax.set_title("Общий уровень по классам")
ax.legend()
for b, i in zip(bars, order):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{avg_by_class[i]:.0f}%",
            ha="center", size=9)
fig.tight_layout()
fig.savefig(FIG / "classes_overall.png", dpi=150, bbox_inches="tight")
plt.close()

print("Saved charts to", FIG)
