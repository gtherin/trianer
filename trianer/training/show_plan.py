import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .plan import get_training_plan
from ..core import theme


def get_label(v):
    if v == 0:
        return ""
    if v < 60:
        return f"{v:.0f}s"
    if v > 3600:
        v /= 60
        h, m = v / 60, v % 60
        return f"{h:.0f}h{m:02.0f}" if m != 0 else f"{h:.0f}h"
    m, s = v / 60, v % 60
    return f"{m:.0f}m{s:02.0f}" if s != 0 else f"{m:.0f}m"


def plot_rectangle(ax, x_coo, y_coo, width, color, label, fontsize=8):
    ywidth = 0.6
    ax.add_patch(Rectangle((x_coo, y_coo), width, ywidth, color=color))
    r, g, b, _ = color
    text_color = "white" if type(color) == str or r * g * b < 0.5 else "darkgrey"
    rotation = 90 if width < 201 else 0
    cywidth = 0.5 * ywidth if width < 201 else 0.4 * ywidth
    ax.annotate(
        label,
        (x_coo + 0.5 * width, y_coo + cywidth),
        color=text_color,
        fontsize=fontsize,
        ha="center",
        va="center",
        rotation=rotation,
    )


def show_plan(plan):
    data = get_training_plan(plan)
    data["ds"] = data["duration"].dt.seconds
    data["rpace"] = data["pace"].dt.ceil(freq="30S")
    data["space"] = data["rpace"].astype(str).str[10:]

    data["sess_label"] = data["week"].apply(lambda x: f"w={x:2.0f},s=")
    data["sess_label"] += data.groupby("week")["dtime"].transform("rank", method="dense", ascending=False).astype(str)

    fig, ax = plt.subplots(figsize=(10, 15))
    gdf = data.groupby("dtime")
    number_of_days = len(gdf.size())
    ax.set_xlim([0, gdf["ds"].sum().max()])
    ax.set_ylim([0, number_of_days + 1])
    ywidth = 0.6

    spaces = sorted(data["space"].unique())
    colors = dict(zip(spaces, plt.colormaps["RdYlGn"](np.linspace(0.1, 0.95, len(spaces)))))

    y_coo = 0
    ylabels = []
    for d, tdf in data.groupby("dtime"):
        x_coo = 0
        for _, a in tdf.iterrows():
            width = np.max([a["ds"], 200])
            if "10-20-30" in a.training and a["ds"] == 300:
                plot_rectangle(ax, x_coo, y_coo, width, "pink", get_label(a["ds"]))
            else:
                plot_rectangle(ax, x_coo, y_coo, width, colors[a["space"]], get_label(a["ds"]))
            x_coo += width
        y_coo += 1
        ylabels.append(tdf["sess_label"].iloc[0])

    x_coo, width = 0, ax.get_xlim()[1] / len(colors)
    for s, c in colors.items():
        plot_rectangle(ax, x_coo, y_coo, width, c, s, fontsize=20)
        x_coo += width

    ax.set_yticks(np.array(range(number_of_days)) + 0.5 * ywidth)
    ax.set_yticklabels(ylabels)
    ax.xaxis.set_visible(False)
    plt.show()
