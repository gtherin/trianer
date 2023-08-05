import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from . import average


def plot_data(data, in_column=False):
    # Plot the time evolution data
    norm = average.get_data()

    data["bmr"] = (-161.0 * data["is_woman"]).fillna(5.0)
    data["bmr"] = 10.0 * data["weight_kg"] + 6.25 * data["height_cm"] - 5.0 * data["age"] + data["bmr"]

    norm["bmr"] = (-161.0 * norm["is_woman"]).fillna(5.0)
    norm["bmr"] = 10.0 * norm["weight_kg"] + 6.25 * norm["height_cm"] - 5.0 * norm["age"] + norm["bmr"]

    if in_column:
        fig, ax = plt.subplots(4, 1, figsize=(8, 20))
    else:
        fig, tax = plt.subplots(2, 2, figsize=(15, 10))
        ax = [tax[0][0], tax[0][1], tax[1][0], tax[0][1]]

    quantities = [
        ["height_cm", "Taille (cm)"],
        ["weight_kg", "Poids (kg)"],
        ["IMC", "IMC"],
        ["bmr", "Metabolisme de base"],
    ]
    for name, df in data.groupby("name"):
        df["slope"] = data["height_cm"].diff() / data["age"].diff()
        reg = LinearRegression().fit(df[["age"]], df["height_cm"])
        last_slope = df["slope"].ewm(3).mean().iloc[-1]
        print(f"{name} grandit en moyenne de {reg.coef_[0]:.2f} cm par an ({last_slope:.1f})")
        for n, q in enumerate(quantities):
            ax[n].plot(df["age"], df[q[0]], label=name)
        print(df)

    for name, df in norm.groupby("name"):
        for n, q in enumerate(quantities):
            ax[n].fill_between(df["age"], df[q[0]] * 0.9, df[q[0]] * 1.1, label=name, alpha=0.1)
            ax[n].set_ylabel(q[1])
            ax[n].set_xlabel("Age (années)")

    plt.legend()

    return fig


def get_bmr(weight, height, age, is_woman):
    s = -161 if is_woman else 5
    bmr = 10.0 * weight + 6.25 * height - 5.0 * age + s
    bmr2 = 11.9 * weight + 0.84 * height + 579
    # print(f"{name} BMR={bmr:.0f} kcal, {bmr2:.0f} kcal (poids={weight} kg, taille={height} cm)")
    return bmr
