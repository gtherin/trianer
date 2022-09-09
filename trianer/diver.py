import pandas as pd
import numpy as np
import scipy as sp

from scipy import ndimage

import uncertainties as unc
from uncertainties.umath import log
from scipy.optimize import minimize_scalar, minimize

# gravity acceleration
g = 9.80665  # m/s2

# density of the water
r_water = 1025  # kg/m3
pressure_0 = 101325  # Pa

# density of the ballast (lead)
r_ballast = 11000  # kg/m3
# density of the neoprene
r_neo = 1230  # kg/m3
# density of neoprene foam
r_nfoam = 170  # kg/m3


# General constants
rho = 1025
rhob = 11000
rhon = 1230
rhonf = 170


def get_body_surface_area(height: float, weight: float) -> float:
    """
    height : height of the person in cm
    weight : weight of the person in kg

    return body_surface_area in m**2
    """

    # For the record, surface of the body parts with no swimsuit (head 9%, hands:2x1%, feet:2x1.5%)
    # Formule de Shuter et Aslani
    return 0.00949 * (height ** 0.655) * (weight ** 0.441)


def get_trajectory(time_descent, time_ascent, max_depth) -> pd.Series:
    x = np.arange(0, time_descent)
    y = -max_depth * np.arange(0, time_descent) / time_descent
    # y = -np.log10((np.cosh((x - 1) / 40) + 1))
    # y = max_depth * (y - y[0]) / np.abs(y[-1] - y[0])

    x2 = np.arange(0, time_ascent) + time_descent
    y2 = max_depth * np.arange(0, time_ascent) / time_ascent - max_depth

    x3 = np.append(x, x2)
    y3 = np.append(y, y2)
    return pd.Series(y3, index=x3)


def get_volume_tissues(weight_body, weight_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the volume occupied by tissue of the freediver body from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.

    weight_body    = mass of the body
    weight_ballast : mass of the ballast
    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = depth_gliding_descent +- error
    depth_eq_a   = depth_gliding_ascent +- error

    return tissues volume +- error
    """
    Vt = (
        weight_ballast
        - (weight_ballast * r_water) / r_ballast
        - (
            -(
                weight_body
                * (pressure_0 + depth_eq_a * g * r_water)
                * (pressure_0 + depth_eq_d * g * r_water)
                * r_neo
                * (speed_a ** 2 + speed_d ** 2)
            )
            + pressure_0
            * r_water
            * r_neo
            * (
                (pressure_0 + depth_eq_a * g * r_water) * speed_a ** 2
                + (pressure_0 + depth_eq_d * g * r_water) * speed_d ** 2
            )
            * volume_gas
            + (
                (pressure_0 + depth_eq_a * g * r_water)
                * (pressure_0 * r_neo * (r_water - r_nfoam) + depth_eq_d * g * r_water * (r_water - r_neo) * r_nfoam)
                * speed_a ** 2
                + (pressure_0 + depth_eq_d * g * r_water)
                * (pressure_0 * r_neo * (r_water - r_nfoam) + depth_eq_a * g * r_water * (r_water - r_neo) * r_nfoam)
                * speed_d ** 2
            )
            * volume_suit
        )
        / (
            (pressure_0 + depth_eq_a * g * r_water)
            * (pressure_0 + depth_eq_d * g * r_water)
            * r_neo
            * (speed_a ** 2 + speed_d ** 2)
        )
    ) / r_water
    return Vt


def get_drag_coefficient(volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the hydrodynamic drag coefficient (drag = C*speed**2) from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.

    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part) part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = depth_gliding_descent +- error
    depth_eq_a   = depth_gliding_ascent +- error

    """

    speed2 = speed_a ** 2 + speed_d ** 2
    mass_toid = r_neo * (volume_gas + volume_suit) - r_nfoam * volume_suit
    volume_toid = mass_toid / r_neo

    pressure_eq_a = pressure_0 + depth_eq_a * g * r_water
    pressure_eq_d = pressure_0 + depth_eq_d * g * r_water

    deltax_eq_a = pressure_eq_a / g / r_water
    deltax_eq_d = pressure_eq_d / g / r_water

    C = -(depth_eq_a - depth_eq_d) * pressure_0 * volume_toid / (deltax_eq_a * deltax_eq_d * speed2)
    return C


def get_total_work(
    depth_max,
    mass_body,
    mass_ballast,
    volume_incompress,
    volume_suit,
    volume_gas,
    speed_d,
    speed_a,
    drag_coefficient,
):
    """Calculation of the mechanical work spent for the descent

    depth_max   = depth_max
    weight_body    = mass of the body
    weight_ballast : mass of the ballast
    volume_incompress   = get_volume_tissues(weight_body, weight_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a) : volume of the incompressible (liquid and solid part) part of the body
    volume_suit   = volume of the suit
    volume_gas   = volume_lungs : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descet speed : descent speed
    speed_a   = ascent speed : ascension speed
    drag_coefficient : hydrodynamic drag constant
    """

    force_weight = g * (mass_body + mass_ballast + rhonf * volume_suit)
    force_archimede1 = g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
    force_archimede2 = g * rho * (volume_gas + (1 - rhonf / rhon) * volume_suit)

    force_drag_d = drag_coefficient * speed_d ** 2
    force_drag_a = drag_coefficient * speed_a ** 2

    force_d = force_drag_d - force_weight + force_archimede1
    force_a = force_drag_a + force_weight - force_archimede1

    work = depth_max * force_a + pressure_0 * (
        +force_a
        - force_d
        - 2 * force_archimede2
        - force_archimede2 * log(1 + (depth_max * g * rho) / pressure_0)
        + force_archimede2 * log(force_archimede2 / force_a)
        + force_archimede2 * log(-force_archimede2 / force_d)
    ) / (g * rho)
    return work


class Diver:
    def __init__(self, data: dict) -> None:
        """
        m : mass of the body
        M : mass of the body + ballast + suit
        mb : mass of the ballast
        ms : mass of the suit
        Vt : volume of the incompressible (liquid and solid part) part of the body
        Vg : volume of the compressible (gaseous part)  part of the body at p_0 pressure
        Vb : volume of the ballast
        Vs : volume of the suit
        Vsi : volume of the suit incompressible
        Vsg : volume of the suit gaseous
        vD : descent speed
        vA : ascension speed
        CC : hydrodynamic drag constant

        """

        self.data = data
        for c in ["surname", "depth_max", "speed_descent", "speed_ascent"]:
            setattr(self, c, data[c])

    def get_drag_force(self) -> None:

        Vs_U = self.data["volume_suit"]
        Vg_U = self.data["volume_lungs"]
        depth_gliding_descent = unc.ufloat(
            self.data["depth_gliding_descent"], self.data["depth_gliding_descent_error"]
        )
        depth_gliding_ascent = unc.ufloat(self.data["depth_gliding_ascent"], self.data["depth_gliding_ascent_error"])

        # Drag constant estimation
        C_U = get_drag_coefficient(
            Vs_U, Vg_U, self.speed_descent, self.speed_ascent, depth_gliding_descent, depth_gliding_ascent
        )
        self.data["drag constant"] = C_U.n
        self.data["error drag constant"] = C_U.s

        return C_U

    def minimize(self, method=None) -> None:

        weight_body = self.data["weight_body"]
        weight_ballast = self.data["weight_ballast"]
        volume_suit = self.data["volume_suit"]
        volume_lungs = self.data["volume_lungs"]
        depth_gliding_descent = unc.ufloat(
            self.data["depth_gliding_descent"], self.data["depth_gliding_descent_error"]
        )
        depth_gliding_ascent = unc.ufloat(self.data["depth_gliding_ascent"], self.data["depth_gliding_ascent_error"])

        # Tissue volume estimation
        volume_tissues = get_volume_tissues(
            weight_body,
            weight_ballast,
            volume_suit,
            volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            depth_gliding_descent,
            depth_gliding_ascent,
        )
        self.data["tissues volume"] = volume_tissues.n
        self.data["error tissues volume"] = volume_tissues.s

        # Drag constant estimation
        drag_coefficient = get_drag_coefficient(
            volume_suit,
            volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            depth_gliding_descent,
            depth_gliding_ascent,
        )

        # Descent work estimation
        total_work = get_total_work(
            self.depth_max,
            weight_body,
            0.0,
            volume_tissues,
            volume_suit,
            volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            drag_coefficient,
        )
        self.data["descent work"] = total_work.n
        self.data["error descent work"] = total_work.s

        # Function to minimize with respect to the user characteristics
        # mb and Tsmm variables to minimize
        # The different versions are used to estimate the uncertainty
        def f(param):
            mb, Tsmm = param
            WDA = get_total_work(
                self.depth_max,
                weight_body,
                mb,
                volume_tissues.n,
                Tsmm / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n,
            )
            return WDA

        def fplusVt(param):
            mb, Tsmm = param
            WDA = get_total_work(
                self.depth_max,
                weight_body,
                mb,
                volume_tissues.n + volume_tissues.s,
                Tsmm / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n,
            )
            return WDA

        def fminusVt(param):
            mb, Tsmm = param
            WDA = get_total_work(
                self.depth_max,
                weight_body,
                mb,
                volume_tissues.n - volume_tissues.s,
                Tsmm / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n,
            )
            return WDA

        def fplusC(param):
            mb, Tsmm = param
            WDA = get_total_work(
                self.depth_max,
                weight_body,
                mb,
                volume_tissues.n,
                Tsmm / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n + drag_coefficient.s,
            )
            return WDA

        def fminusC(param):
            mb, Tsmm = param
            WDA = get_total_work(
                self.depth_max,
                weight_body,
                mb,
                volume_tissues.n,
                Tsmm / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n - drag_coefficient.s,
            )
            return WDA

        # Minimize with bounds
        initial_guess = [1, 1.5]
        bounds = ((0, 5), (0, 10))
        # Working minimization L-BFGS-B, TNC, SLSQP
        res = minimize(f, initial_guess, bounds=bounds, method=method)
        resplusVt = minimize(fplusVt, initial_guess, bounds=bounds, method=method)
        resminusVt = minimize(fminusVt, initial_guess, bounds=bounds, method=method)
        resplusC = minimize(fplusC, initial_guess, bounds=bounds, method=method)
        resminusC = minimize(fminusC, initial_guess, bounds=bounds, method=method)
        mb_best = res.x[0]
        Tsmm_best = res.x[1]
        mb_plusVt = resplusVt.x[0]
        Tsmm_plusVt = resplusVt.x[1]
        mb_minusVt = resminusVt.x[0]
        Tsmm_minusVt = resminusVt.x[1]
        mb_plusC = resplusC.x[0]
        Tsmm_plusC = resplusC.x[1]
        mb_minusC = resminusC.x[0]
        Tsmm_minusC = resminusC.x[1]

        mb_mean = (mb_plusVt + mb_minusVt + mb_plusC + mb_minusC) / 4
        mb_err = np.sqrt((mb_mean - mb_plusVt) ** 2 + (mb_mean - mb_plusC) ** 2)
        Tsmm_mean = (Tsmm_plusVt + Tsmm_minusVt + Tsmm_plusC + Tsmm_minusC) / 4
        Tsmm_err = np.sqrt((Tsmm_mean - Tsmm_plusVt) ** 2 + (Tsmm_mean - Tsmm_plusC) ** 2)

        mb_EXP = unc.ufloat(mb_mean, mb_err)
        Tsmm_EXP = unc.ufloat(Tsmm_mean, Tsmm_err)

        # Performance gain
        gain = (
            get_total_work(
                self.depth_max,
                weight_body,
                mb_EXP,
                volume_tissues.n,
                Tsmm_EXP / 1000 * 2,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n,
            )
            - get_total_work(
                self.depth_max,
                weight_body,
                weight_ballast,
                volume_tissues.n,
                volume_suit,
                volume_lungs,
                self.speed_descent,
                self.speed_ascent,
                drag_coefficient.n,
            )
        ) / get_total_work(
            self.depth_max,
            weight_body,
            weight_ballast,
            volume_tissues.n,
            volume_suit,
            volume_lungs,
            self.speed_descent,
            self.speed_ascent,
            drag_coefficient.n,
        )

        print("Best ballast weight (Kg) \t\t= ", mb_best)
        print("Average optimal ballast weight (Kg) \t= ", mb_EXP)
        print("Best suite thickness (mm) \t\t= ", Tsmm_best)
        print("Average optimal suite thickness (mm) \t= ", Tsmm_EXP)
        print("")
        print("Performance gain =", gain * 100, "%")

    def show(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle
        from matplotlib.patheffects import withStroke
        from matplotlib.ticker import AutoMinorLocator, MultipleLocator

        royal_blue = [0, 20 / 256, 82 / 256]

        X = np.linspace(0.5, 3.5, 100)
        Y1 = 3 + np.cos(X)
        Y2 = 1 + np.cos(1 + X / 0.75) / 2
        Y3 = np.random.uniform(Y1, Y2, len(X))

        fig, ax = plt.subplots(figsize=(15, 5))

        ax.tick_params(which="major", width=1.0, length=10, labelsize=14)
        ax.tick_params(which="minor", width=1.0, length=5, labelsize=10, labelcolor="0.25")

        ax.grid(linestyle="--", linewidth=0.5, color=".25", zorder=-10)

        # ax.plot(X, Y1, c="C0", lw=2.5, label="Blue signal", zorder=10)

        max_depth = 125  # in m
        time_descent = 120  # in sec
        time_ascent = 94  # in sec

        track = get_trajectory(time_descent, time_ascent, max_depth)

        ydee = 27.5
        xdee = track[track + ydee < 0].index[0]

        yaee = 7.5
        xaee = track[track + yaee < 0].index[-1]

        track1 = np.ma.masked_where(track.index <= xdee, track)
        track2 = np.ma.masked_where((track.index > xdee) & (track.index < xaee), track)

        ax.plot(track.index, track1, track.index, track2, lw=2.5)

        ax.set_title(f"Position-time estimation of {self.surname}", fontsize=20, verticalalignment="bottom")
        ax.set_xlabel("Time in seconds", fontsize=14)
        ax.set_ylabel("Depth in meters", fontsize=14)

        def annotate(x, y, text):
            ax.add_artist(
                Circle(
                    (x, y),
                    radius=10.15,
                    clip_on=False,
                    linewidth=2.5,
                    edgecolor=royal_blue + [0.6],
                    facecolor="none",
                    path_effects=[withStroke(linewidth=7, foreground="white")],
                )
            )

            ax.text(
                x,
                y - 0.2,
                text,
                ha="center",
                va="top",
                weight="bold",
                color=royal_blue,
            )

        annotate(xdee, -ydee, "Equilibrium")
        annotate(xaee, -yaee, "Equilibrium")

        # newax = fig.add_axes([0.2, 0.2, 0.1, 0.1], anchor="NE")
        # newax.imshow(plt.imread("diver.png"))
        # newax.axis("off")

        newax = fig.add_axes([0.3, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread("diver.png"), 50))
        newax.axis("off")

        newax = fig.add_axes([0.6, 0.33, 0.15, 0.15], anchor="NE")
        newax.imshow(sp.ndimage.rotate(plt.imread("diver.png"), 130))
        newax.axis("off")

        plt.show()
