import streamlit as st

from .variables import variables


def get_var_slider(key, **kwargs):
    return variables[key].get_input(st.slider, **kwargs)


def get_var_expander(key, **kwargs):
    return variables[key].get_input(st.expander, **kwargs)


def get_var_number(key, **kwargs):
    return variables[key].get_input(st.number_input, **kwargs)


def get_var_selectbox(key, **kwargs):
    return variables[key].get_input(st.selectbox, **kwargs)


def get_var_radio(key, **kwargs):
    return variables[key].get_input(st.radio, **kwargs)


def get_var_date(key, **kwargs):
    return variables[key].get_input(st.date_input, **kwargs)


def get_var_multiselect(key, **kwargs):
    return variables[key].get_input(st.multiselect, **kwargs)


def get_value(key):
    return variables[key].get_init_value()
