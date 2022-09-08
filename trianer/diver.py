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
p_0 = 101325  # Pa

# density of the ballast (lead)
r_ballast = 11000  # kg/m3
# density of the neoprene
r_neo = 1230  # kg/m3
# density of neoprene foam
r_nfoam = 170  # kg/m3


# General constants
rho = 1025
P0 = 101325
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


def get_trajectory(descent_time, ascent_time, max_depth) -> pd.Series:
    x = np.arange(0, descent_time)
    y = -max_depth * np.arange(0, descent_time) / descent_time
    # y = -np.log10((np.cosh((x - 1) / 40) + 1))
    # y = max_depth * (y - y[0]) / np.abs(y[-1] - y[0])

    x2 = np.arange(0, ascent_time) + descent_time
    y2 = max_depth * np.arange(0, ascent_time) / ascent_time - max_depth

    x3 = np.append(x, x2)
    y3 = np.append(y, y2)
    return pd.Series(y3, index=x3)


def Vt_EXP(mass_body, mass_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the volume occupied by tissue of the freediver body from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.

    mass_body    = body mass : mass of the body
    mass_ballast   = ballast mass : mass of the ballast
    volume_suit   = suite volume : volume of the suit
    volume_gas   = gas volume : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = descent eq. depth +- error
    depth_eq_a   = ascent eq. depth +- error

    return tissues volume +- error
    """
    Vt = (
        mass_ballast
        - (mass_ballast * r_water) / r_ballast
        - (
            -(
                mass_body
                * (p_0 + depth_eq_a * g * r_water)
                * (p_0 + depth_eq_d * g * r_water)
                * r_neo
                * (speed_a ** 2 + speed_d ** 2)
            )
            + p_0
            * r_water
            * r_neo
            * ((p_0 + depth_eq_a * g * r_water) * speed_a ** 2 + (p_0 + depth_eq_d * g * r_water) * speed_d ** 2)
            * volume_gas
            + (
                (p_0 + depth_eq_a * g * r_water)
                * (p_0 * r_neo * (r_water - r_nfoam) + depth_eq_d * g * r_water * (r_water - r_neo) * r_nfoam)
                * speed_a ** 2
                + (p_0 + depth_eq_d * g * r_water)
                * (p_0 * r_neo * (r_water - r_nfoam) + depth_eq_a * g * r_water * (r_water - r_neo) * r_nfoam)
                * speed_d ** 2
            )
            * volume_suit
        )
        / ((p_0 + depth_eq_a * g * r_water) * (p_0 + depth_eq_d * g * r_water) * r_neo * (speed_a ** 2 + speed_d ** 2))
    ) / r_water
    return Vt


def C_EXP(volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a):
    """Calculation of the hydrodynamic drag coefficient (drag = C*speed**2) from
    the descent and ascent critical depth, the depths where the diver stop to swim and start to glide.



    volume_suit   = suite volume : volume of the suit
    volume_gas   = gas volume : volume of the compressible (gaseous part) part of the body at p_0 pressure
    speed_d   = descent speed
    speed_a   = ascension speed
    depth_eq_d   = descent eq. depth +- error
    depth_eq_a   = ascent eq. depth +- error
    """

    C = -(
        (
            (depth_eq_a - depth_eq_d)
            * g ** 2
            * p_0
            * r_water ** 2
            * (r_neo * (volume_gas + volume_suit) - r_nfoam * volume_suit)
        )
        / ((p_0 + depth_eq_a * g * r_water) * (p_0 + depth_eq_d * g * r_water) * r_neo * (speed_a ** 2 + speed_d ** 2))
    )
    return C


def WDAComp2(depth_max, mass_body, mass_ballast, volume_incompress, volume_suit, volume_gas, speed_d, speed_a, CC):
    """Calculation of the mechanical work spent for the descent

    WD_U = WDAComp(depth_max, mass_body, 0.0, Vt_U, volume_suit, volume_gas, speed_d, speed_a, C_U)

    depth_max   = final depth
    mass_body    = body mass : mass of the body
    mass_ballast   = ballast mass : mass of the ballast
    volume_incompress   = Vt_EXP(mass_body, mass_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a) : volume of the incompressible (liquid and solid part) part of the body
    volume_suit   = suite volume : volume of the suit
    volume_gas   = gas volume : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descet speed : descent speed
    speed_a   = ascent speed : ascension speed
    CC   = C_EXP(volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a) : hydrodynamic drag constant
    """

    mass_suit = r_nfoam * volume_suit
    mass_total = mass_body + mass_ballast + mass_suit

    WDA = (
        depth_max
        * (
            CC * speed_a ** 2
            + g * mass_total
            - g * r_water * (mass_ballast / r_ballast + mass_suit / r_neo + volume_incompress)
        )
        - (
            p_0
            * (
                -(CC * speed_a ** 2)
                - g * mass_total
                + g
                * r_water
                * (
                    mass_ballast / r_ballast
                    + volume_incompress
                    + mass_suit / r_neo
                    + (1 - r_nfoam / r_neo) * volume_suit
                    + volume_incompress
                )
            )
        )
        / (g * r_water)
        + (
            p_0
            * (
                CC * speed_d ** 2
                - g * mass_total
                + g * r_water * (mass_ballast / r_ballast + mass_suit / r_neo + volume_incompress)
            )
            * (
                CC * speed_d ** 2
                - g * mass_total
                + g
                * r_water
                * (
                    mass_ballast / r_ballast
                    + volume_gas
                    + mass_suit / r_neo
                    + (1 - r_nfoam / r_neo) * volume_suit
                    + volume_incompress
                )
            )
        )
        / (
            g
            * r_water
            * (
                -(CC * speed_d ** 2)
                + g * mass_total
                - g * r_water * (mass_ballast / r_ballast + mass_suit / r_neo + volume_incompress)
            )
        )
        - p_0 * (volume_gas + (1 - r_nfoam / r_neo) * volume_suit) * log(1 + (depth_max * g * r_water) / p_0)
        + p_0
        * (volume_gas + (1 - r_nfoam / r_neo) * volume_suit)
        * log(
            1
            + (
                -(CC * speed_a ** 2)
                - g * mass_total
                + g
                * r_water
                * (
                    mass_ballast / r_ballast
                    + volume_gas
                    + mass_suit / r_neo
                    + (1 - r_nfoam / r_neo) * volume_suit
                    + volume_incompress
                )
            )
            / (
                CC * speed_a ** 2
                + g * mass_total
                - g * r_water * (mass_ballast / r_ballast + mass_suit / r_neo + volume_incompress)
            )
        )
        + p_0
        * (volume_gas + (1 - r_nfoam / r_neo) * volume_suit)
        * log(
            1
            + (
                CC * speed_d ** 2
                - g * mass_total
                + g
                * r_water
                * (
                    mass_ballast / r_ballast
                    + volume_gas
                    + mass_suit / r_neo
                    + (1 - r_nfoam / r_neo) * volume_suit
                    + volume_incompress
                )
            )
            / (
                -(CC * speed_d ** 2)
                + g * mass_total
                - g * r_water * (mass_ballast / r_ballast + mass_suit / r_neo + volume_incompress)
            )
        )
    )
    return WDA


# def WDAComp2(depth_max, mass_body, mass_ballast, volume_incompress, volume_suit, volume_gas, speed_d, speed_a, CC):
def WDAComp(DD, mass_body, mass_ballast, volume_incompress, volume_suit, volume_gas, vD, vA, CC):
    """Calculation of the mechanical work spent for the descent

    WD_U = WDAComp(depth_max, mass_body, 0.0, Vt_U, volume_suit, volume_gas, speed_d, speed_a, C_U)

    depth_max   = final depth
    mass_body    = body mass : mass of the body
    mass_ballast   = ballast mass : mass of the ballast
    volume_incompress   = Vt_EXP(mass_body, mass_ballast, volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a) : volume of the incompressible (liquid and solid part) part of the body
    volume_suit   = suite volume : volume of the suit
    volume_gas   = gas volume : volume of the compressible (gaseous part)  part of the body at p_0 pressure
    speed_d   = descet speed : descent speed
    speed_a   = ascent speed : ascension speed
    CC   = C_EXP(volume_suit, volume_gas, speed_d, speed_a, depth_eq_d, depth_eq_a) : hydrodynamic drag constant
    """

    WDA = (
        DD
        * (
            CC * vA ** 2
            + g * (mass_body + mass_ballast + rhonf * volume_suit)
            - g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
        )
        - (
            P0
            * (
                -(CC * vA ** 2)
                - g * (mass_body + mass_ballast + rhonf * volume_suit)
                + g
                * rho
                * (
                    mass_ballast / rhob
                    + volume_gas
                    + (rhonf * volume_suit) / rhon
                    + (1 - rhonf / rhon) * volume_suit
                    + volume_incompress
                )
            )
        )
        / (g * rho)
        + (
            P0
            * (
                CC * vD ** 2
                - g * (mass_body + mass_ballast + rhonf * volume_suit)
                + g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
            )
            * (
                CC * vD ** 2
                - g * (mass_body + mass_ballast + rhonf * volume_suit)
                + g
                * rho
                * (
                    mass_ballast / rhob
                    + volume_gas
                    + (rhonf * volume_suit) / rhon
                    + (1 - rhonf / rhon) * volume_suit
                    + volume_incompress
                )
            )
        )
        / (
            g
            * rho
            * (
                -(CC * vD ** 2)
                + g * (mass_body + mass_ballast + rhonf * volume_suit)
                - g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
            )
        )
        - P0 * (volume_gas + (1 - rhonf / rhon) * volume_suit) * log(1 + (DD * g * rho) / P0)
        + P0
        * (volume_gas + (1 - rhonf / rhon) * volume_suit)
        * log(
            1
            + (
                -(CC * vA ** 2)
                - g * (mass_body + mass_ballast + rhonf * volume_suit)
                + g
                * rho
                * (
                    mass_ballast / rhob
                    + volume_gas
                    + (rhonf * volume_suit) / rhon
                    + (1 - rhonf / rhon) * volume_suit
                    + volume_incompress
                )
            )
            / (
                CC * vA ** 2
                + g * (mass_body + mass_ballast + rhonf * volume_suit)
                - g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
            )
        )
        + P0
        * (volume_gas + (1 - rhonf / rhon) * volume_suit)
        * log(
            1
            + (
                CC * vD ** 2
                - g * (mass_body + mass_ballast + rhonf * volume_suit)
                + g
                * rho
                * (
                    mass_ballast / rhob
                    + volume_gas
                    + (rhonf * volume_suit) / rhon
                    + (1 - rhonf / rhon) * volume_suit
                    + volume_incompress
                )
            )
            / (
                -(CC * vD ** 2)
                + g * (mass_body + mass_ballast + rhonf * volume_suit)
                - g * rho * (mass_ballast / rhob + (rhonf * volume_suit) / rhon + volume_incompress)
            )
        )
    )
    return WDA


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

        Ss: suit surface assumption: 2 m2
        """

        # Get suite volume in m3
        Ts = data["thickness suite"] / 1000.0
        Ss = 2  # Surface suite (m2)
        data["suite volume"] = Ss * Ts

        # Get gas volume in m3 from l
        data["gas volume"] /= 1000

        self.data = data
        self.name = data["name"]

        D_U = self.data["final depth"]
        m_U = self.data["body mass"]
        mb_U = self.data["ballast mass"]
        Vs_U = self.data["suite volume"]
        Vg_U = self.data["gas volume"]
        vD_U = self.data["descet speed"]
        vA_U = self.data["ascent speed"]
        dD_U = unc.ufloat(self.data["descent eq. depth"], self.data["error descent eq. depth"])
        dA_U = unc.ufloat(self.data["ascent eq. depth"], self.data["error ascent eq. depth"])

        # Tissue volume estimation
        Vt_U = Vt_EXP(m_U, mb_U, Vs_U, Vg_U, vD_U, vA_U, dD_U, dA_U)
        self.data["tissues volume"] = Vt_U.n
        self.data["error tissues volume"] = Vt_U.s

        # Drag constant estimation
        C_U = C_EXP(Vs_U, Vg_U, vD_U, vA_U, dD_U, dA_U)
        self.data["drag constant"] = C_U.n
        self.data["error drag constant"] = C_U.s

        # Descent work estimation
        WD_U = WDAComp(D_U, m_U, 0.0, Vt_U, Vs_U, Vg_U, vD_U, vA_U, C_U)
        self.data["descent work"] = WD_U.n
        self.data["error descent work"] = WD_U.s

    def minimize(self, method=None) -> None:

        D_U = self.data["final depth"]
        m_U = self.data["body mass"]
        mb_U = self.data["ballast mass"]
        Vs_U = self.data["suite volume"]
        Vg_U = self.data["gas volume"]
        vD_U = self.data["descet speed"]
        vA_U = self.data["ascent speed"]
        dD_U = unc.ufloat(self.data["descent eq. depth"], self.data["error descent eq. depth"])
        dA_U = unc.ufloat(self.data["ascent eq. depth"], self.data["error ascent eq. depth"])

        # Tissue volume estimation
        Vt_U = Vt_EXP(m_U, mb_U, Vs_U, Vg_U, vD_U, vA_U, dD_U, dA_U)
        self.data["tissues volume"] = Vt_U.n
        self.data["error tissues volume"] = Vt_U.s

        # Drag constant estimation
        C_U = C_EXP(Vs_U, Vg_U, vD_U, vA_U, dD_U, dA_U)
        self.data["drag constant"] = C_U.n
        self.data["error drag constant"] = C_U.s

        # Descent work estimation
        WD_U = WDAComp(D_U, m_U, 0.0, Vt_U, Vs_U, Vg_U, vD_U, vA_U, C_U)
        self.data["descent work"] = WD_U.n
        self.data["error descent work"] = WD_U.s

        # Function to minimize with respect to the user characteristics
        # mb and Tsmm variables to minimize
        # The different versions are used to estimate the uncertainty
        def f(param):
            mb, Tsmm = param
            WDA = WDAComp(D_U, m_U, mb, Vt_U.n, Tsmm / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n)
            return WDA

        def fplusVt(param):
            mb, Tsmm = param
            WDA = WDAComp(D_U, m_U, mb, Vt_U.n + Vt_U.s, Tsmm / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n)
            return WDA

        def fminusVt(param):
            mb, Tsmm = param
            WDA = WDAComp(D_U, m_U, mb, Vt_U.n - Vt_U.s, Tsmm / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n)
            return WDA

        def fplusC(param):
            mb, Tsmm = param
            WDA = WDAComp(D_U, m_U, mb, Vt_U.n, Tsmm / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n + C_U.s)
            return WDA

        def fminusC(param):
            mb, Tsmm = param
            WDA = WDAComp(D_U, m_U, mb, Vt_U.n, Tsmm / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n - C_U.s)
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
            WDAComp(D_U, m_U, mb_EXP, Vt_U.n, Tsmm_EXP / 1000 * 2, Vg_U, vD_U, vA_U, C_U.n)
            - WDAComp(D_U, m_U, mb_U, Vt_U.n, Vs_U, Vg_U, vD_U, vA_U, C_U.n)
        ) / WDAComp(D_U, m_U, mb_U, Vt_U.n, Vs_U, Vg_U, vD_U, vA_U, C_U.n)

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
        descent_time = 120  # in sec
        ascent_time = 94  # in sec

        track = get_trajectory(descent_time, ascent_time, max_depth)

        ydee = 27.5
        xdee = track[track + ydee < 0].index[0]

        yaee = 7.5
        xaee = track[track + yaee < 0].index[-1]

        track1 = np.ma.masked_where(track.index <= xdee, track)
        track2 = np.ma.masked_where((track.index > xdee) & (track.index < xaee), track)

        ax.plot(track.index, track1, track.index, track2, lw=2.5)

        ax.set_title(f"Position-time estimation of {self.name}", fontsize=20, verticalalignment="bottom")
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
