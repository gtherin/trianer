import matplotlib.pyplot as plt

from .labels import gl, gc


background_color = "#e6dce2"  # cdcdcd
background_color2 = "#f5edf2"


def get_color(discipline):
    colors = {
        "swimming": "#581845",
        "cycling": "#C70039",
        "running": "#FF5733",
        "kcalories": "purple",
        "caloric_balance": "purple",
        "hydric_balance": "darkcyan",
        "hydration_ideal": "green",
        "ihydration": "green",
        "hydration": "darkcyan",
        "transition 1": "#cdcdcd",
        "transition 2": "#cdcdcd",
        "The end": "#000639",
        "axis": "#C70039",
    }
    return colors[discipline] if discipline in colors else "black"


temperature_color = "#FFC300"


def roadmap_highlight(s):
    color = get_color(gc(s.Discipline))
    if s.Discipline in [gl("cycling"), gl("running"), gl("swimming")]:
        return [f"background-color: {color}22;color: {color}; font-weight: bolder"] * len(s)
    elif "transition" in s.Discipline:
        return [f"background-color: {color}22;color: white; font-weight: bolder"] * len(s)
    elif s.Discipline == "The end":
        return ["background-color: #000639;color: red; font-weight: bolder"] * len(s)
    else:
        return ["background-color: white"] * len(s)


roadmap_progress_bar = ["Red", get_color("The end")]

slope_range_colors = [background_color, "#f08205DD"]
title_color = get_color("swimming")
danger_color = "#FF5733"
# danger_color = "red"


def get_ravitos_styles(ravito):
    return dict(
        color="purple" if "org" in ravito["fooding"] else "darkcyan",
        lw=4 if "org" in ravito["fooding"] else 4,
        alpha=0.5,
    )


def set_style():
    plt.rcParams["axes.edgecolor"] = get_color("axis")
    plt.rcParams["axes.labelcolor"] = get_color("axis")
    plt.rcParams["axes.titlecolor"] = get_color("axis")
    plt.rcParams["axes.facecolor"] = background_color
    plt.rcParams["figure.edgecolor"] = get_color("axis")
    plt.rcParams["figure.facecolor"] = background_color
    # plt.rcParams["grid.color"] = "white"
    plt.rcParams["legend.facecolor"] = background_color
    plt.rcParams["legend.edgecolor"] = background_color
    # plt.rcParams["text.color"] = "white"
    plt.rcParams["xtick.color"] = get_color("axis")
    plt.rcParams["ytick.color"] = get_color("axis")

    plt.rcParams["font.size"] = 16
    # plt.rcParams["axes.labelsize"] = "medium"
    plt.rcParams["lines.linewidth"] = 4

    from cycler import cycler

    # mpl.rcParams['axes.prop_cycle'] = cycler(color='bgrcmyk')
    # mpl.rcParams['axes.prop_cycle'] = cycler(color='bgrcmyk')
    plt.rcParams["axes.prop_cycle"] = cycler(
        color=[get_color(c) for c in ["swimming", "cycling", "running", "The end"]]
    )


set_style()
