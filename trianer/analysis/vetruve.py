import numpy as np
from PIL import Image
import random as rd
import matplotlib.pyplot as plt
import os


from .. import nutrition
from ..core.theme import background_color


def hist_calories_per_sport():
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    data = nutrition.get_kcalories(None)
    data["discipline_speed"] = data["discipline"] + "_" + data["speed"].astype(str)
    data2 = data[["discipline_speed", "X kg"]].sort_values("X kg", ascending=False)

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(
        go.Bar(x=data2["discipline_speed"], y=data2["X kg"], name=""),
        secondary_y=False,
    )
    fig.update_layout(autosize=False, width=1200, height=800, title_text="Activity and Calories per kg")
    fig.update_xaxes(title_text="Activity")
    fig.update_yaxes(title_text="calory", secondary_y=False)
    fig.show()


def update_version():
    from ..__version__ import __version__ as pversion

    logs = open("../trianer.wiki/CHANGELOG.md", "r").read().split("####")

    for l in logs:
        if "TODO" not in l and "[" in l:
            break
    version = l[l.find("[") + 1 : l.find("]")]
    with open("trianer/__version__.py", "w") as the_file:
        the_file.write(f"__version__ = '{version}'")

    if pversion == version:
        print(f"Using version {version}")
    else:
        print(f"Update {pversion} => {version}")

    return version


def wordcloud_calories_per_sport(filename=None, generate=True):
    """
    Show activities depending on the calories spent

    """
    plt.figure(figsize=(15, 10))
    if not generate:
        if not os.path.exists(filename):
            filename = "../data/" + filename

        print(f"Read file {filename}")
        import matplotlib.image as mpimg

        wc = mpimg.imread(filename)

    else:
        version = update_version()

        rd.seed(42)

        from wordcloud import WordCloud

        data = nutrition.get_kcalories(None)

        ddata = data.groupby("discipline").mean()
        w = np.round(10 * ddata["X kg"] / ddata["X kg"].max())

        words = []
        for d in ddata.index:
            words += [d] * int(w[d])
        words += [f"v_{version}".replace(".", "_")] * 100

        rd.shuffle(words)

        # read the mask image
        alice_mask = np.array(Image.open("notebooks/vetruve.png"))

        wc = WordCloud(
            background_color=background_color,
            max_words=2000,
            mask=alice_mask,
            contour_width=0,
            contour_color="#f5f4f2",
            repeat=True,
            min_font_size=1,
            colormap="gist_ncar",
        )
        # wc = WordCloud(background_color='white', width=750, height=500)

        # generate word cloud
        wc.generate(" ".join(words))
        if filename:
            print(f"Write in {filename}")
            wc.to_file(filename)

    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    # plt.show()


def generate_version_vetruve():
    filename = "./data/vetruve_gen.png"
    wordcloud_calories_per_sport(filename=filename)
