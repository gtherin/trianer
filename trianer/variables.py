import numpy as np
import datetime


class Variable:
    update_cookie = None
    cookies = {}

    def __init__(self, key=None, srange=None, help=None, label=None, default=None, orange=None) -> None:
        self.key, self.srange, self.help, self.label, self.default = key, srange, help, label, default
        self.orange = orange

    def get_format_value(self, var):
        if self.srange[0] == "t" and type(var) == str and ":" in var:
            dtimes = str(var).split(":")
            return datetime.time(int(dtimes[0]), int(dtimes[1]))
        elif self.srange[0] == "t" and type(var) in [str, int, str]:
            return datetime.time(int(var), 0)
        elif self.srange[0] == "f" and type(var) in [str, int]:
            return float(var)
        elif self.srange[0] == "i" and type(var) in [str, float, int]:
            return int(var)
        else:
            return var

    def get_init_value(self):
        var = Variable.cookies[self.key] if self.key in Variable.cookies else self.default
        return self.get_format_value(var)

    def get_input(self, input_cls):
        import streamlit as st

        kwargs = dict(key=self.key, help=self.help, on_change=lambda: Variable.update_cookie(self.key))
        if input_cls in [st.radio]:
            kwargs.update(dict(horizontal=True))

        if input_cls in [st.selectbox, st.radio]:
            return input_cls(
                self.key if self.label is None else self.label,
                self.srange,
                index=self.srange.index(self.get_init_value()),
                **kwargs
            )

        smin_value, smax_value, sstep = self.get_range_values()

        return input_cls(
            self.key if self.label is None else self.label,
            value=self.get_init_value(),
            min_value=smin_value,
            max_value=smax_value,
            step=sstep,
            **kwargs
        )

    def get_range_values(self):
        stype, smin_value, smax_value, sstep = self.srange.split(":")
        if stype == "t":
            return (
                datetime.time(int(smin_value), 0),
                datetime.time(int(smax_value), 0),
                datetime.timedelta(minutes=int(sstep)),
            )
        elif stype == "i":
            return int(smin_value), int(smax_value), int(sstep)
        elif stype == "f":
            return float(smin_value), float(smax_value), float(sstep)


variables = {
    v["key"]: Variable(**v)
    for v in [
        dict(
            key="swimming_sX100m",
            srange="t:1:5:1",
            help="Swimming pace",
            default=datetime.time(2, 0),
        ),
        dict(
            key="running_sXkm",
            srange="t:3:10:5",
            help="Running pace",
            default=datetime.time(5, 30),
        ),
        dict(
            key="weight_kg",
            srange="i:40:100:1",
            help="Your weight (in kg)",
            default=70,
        ),
        dict(
            key="cycling_kmXh",
            srange="i:16:50:1",
            help="Cylcling speed",
            default=30,
        ),
        dict(
            key="transition_cyc2run_s",
            srange="t:1:5:15",
            help="Transition nat./cycl.",
            default=datetime.time(2, 0),
        ),
        dict(
            key="transition_swi2cyc_s",
            srange="t:1:5:15",
            help="Transition nat./cycl.",
            default=datetime.time(2, 0),
            # orange="r:0.8:1.2:10",  # in relative value, should multiply by current maxdepth
        ),
        dict(
            key="cycling_dplus",
            srange="i:0:5000:10",
            help="Cycling D+",
            default=0,
        ),
        dict(
            key="running_dplus",
            srange="i:0:10000:5",
            help="Running D+",
            default=0,
        ),
        dict(
            key="temperature",
            srange="i:0:40:1",
            help="temperature",
            default=22,
        ),
        dict(
            key="longueur",
            srange=["S", "M", "L", "Half-Ironman", "Ironman"],
            help="Format of the selected race",
            default="L",
        ),
        dict(
            key="race_menu",
            srange=["Existing race", "Existing format", "Personalized"],
            help="Format of the selected race",
            default="Existing race",
        ),
        dict(key="race_default", srange="s", help="Format of the selected race", default="Bois-le-Roi (L)", label=""),
    ]
}


def get_var_slider(key):
    import streamlit as st

    return variables[key].get_input(st.slider)


def get_var_number(key):
    import streamlit as st

    return variables[key].get_input(st.number_input)


def get_var_selectbox(key):
    import streamlit as st

    return variables[key].get_input(st.selectbox)


def get_var_radio(key):
    import streamlit as st

    return variables[key].get_input(st.radio)


def get_value(key):
    import streamlit as st

    return variables[key].get_init_value()


def set_var_on_change_function(update_cookie):
    Variable.update_cookie = update_cookie


def set_var_cookies(cookies):
    Variable.cookies = cookies
