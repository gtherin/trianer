import streamlit as st

from .variables import variables


def get_var_input(key, **kwargs):
    v = variables[key]
    if v.input_format:
        return v.get_input(getattr(st, v.input_format), **kwargs)

    return v.get_input(st.number_input, **kwargs)


def get_value(key):
    return variables[key].get_init_value()
