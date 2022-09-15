import numpy as np
import pandas as pd
from PIL import Image
import random as rd
import matplotlib.pyplot as plt

from wordcloud import WordCloud

# , STOPWORDS

from .fueling import get_kcalories


def hist_calories_per_sport():

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    data = get_kcalories(None)
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


def wordcloud_calories_per_sport():
    """
    Show activities depending on the calories spent

    """

    data = get_kcalories(None)

    ddata = data.groupby("discipline").mean()
    w = np.round(10 * ddata["X kg"] / ddata["X kg"].max())

    words = []
    for d in ddata.index:
        words += [d] * int(w[d])

    rd.shuffle(words)

    # read the mask image
    alice_mask = np.array(Image.open("vetruve.png"))

    plt.figure(figsize=(15, 10))

    wc = WordCloud(
        background_color="white",
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
    wc.to_file("vetruve_gen.png")

    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()
