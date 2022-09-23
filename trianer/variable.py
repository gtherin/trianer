import numpy as np
import datetime


class Variable:
    update_cookie = None
    cookies = {}

    def __init__(
        self, key=None, srange=None, help=None, label=None, default=None, orange=None, input_format=None
    ) -> None:
        self.key, self.srange, self.help, self.label, self.default = key, srange, help, label, default
        self.orange, self.input_format = orange, input_format

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
        elif self.srange[0] == "d" and type(var) in [str, float, int]:
            return int(var)
        elif self.srange[0] == "b" and type(var) in [str, float, int]:
            return bool(var)
        else:
            return var

    def get_key(self):
        return "trianer_" + self.key

    def get_init_value(self):
        var = Variable.cookies[self.get_key()] if self.get_key() in Variable.cookies else self.default
        return self.get_format_value(var)

    def get_input(self, input_cls, **kwargs):
        import streamlit as st

        kwargs.update(dict(key=self.key, help=self.help, on_change=lambda: Variable.update_cookie(self.key)))

        if input_cls in [st.expander]:
            kwargs.update(dict(expanded=self.get_init_value()))
            return input_cls(self.key if self.label is None else self.label, **kwargs)

        smin_value, smax_value, sstep = self.get_range_values()

        if input_cls in [st.radio]:
            kwargs.update(dict(horizontal=True))

        # Set default value
        if input_cls in [st.selectbox, st.radio]:
            kwargs.update(dict(index=self.srange.index(self.get_init_value())))
        elif input_cls in [st.multiselect]:
            kwargs.update(dict(default=self.get_init_value()))
        else:
            kwargs.update(dict(value=self.get_init_value()))

        if input_cls in [st.selectbox, st.radio, st.multiselect]:
            kwargs.update(dict(options=self.srange))

        if input_cls in [st.slider, st.number_input]:
            kwargs.update(dict(min_value=smin_value, max_value=smax_value, step=sstep))
        if input_cls in [st.date_input]:
            kwargs.update(dict(min_value=smin_value, max_value=smax_value))

        if input_cls in [st.date_input]:
            kwargs.update(dict(min_value=smin_value, max_value=smax_value))

        return input_cls(self.key if self.label is None else self.label, **kwargs)

    def get_range_values(self):
        if type(self.srange) == list:
            return [0, 0, 0]

        stype, smin_value, smax_value, sstep = self.srange.split(":")
        if stype == "t":
            return (
                datetime.time(int(smin_value), 0),
                datetime.time(int(smax_value), 0),
                datetime.timedelta(minutes=int(sstep)),
            )
        elif stype == "d":
            return (
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=30),
                1,
            )
        elif stype == "i":
            return int(smin_value), int(smax_value), int(sstep)
        elif stype == "f":
            return float(smin_value), float(smax_value), float(sstep)


def set_var_on_change_function(update_cookie):
    Variable.update_cookie = update_cookie


def set_var_cookies(cookies):
    Variable.cookies = cookies
