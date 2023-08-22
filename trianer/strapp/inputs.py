import streamlit as st
import datetime
import os
import random

from ..core.variables import load_default_data
from ..core.labels import gc
from ..core.variable import Variable


# @st.cache(allow_output_mutation=True, suppress_st_warning=False)
def get_session_id():
    session_id = "TRAINER"  # + datetime.datetime.now().strftime("%H%M%S") + "_" + str(random.randint(0, 1000))
    # st.toast(f"session_id is set to {session_id}", icon="🔆")
    return session_id + "_"


session_id = get_session_id()
variables = load_default_data()


def update_cookie(name):
    try:
        val = st.session_state[name]
        if type(val) == datetime.time:
            fval = str(val)
        elif type(val) == str:
            fval = gc(val)
        elif type(val) == list and (type(val[0]) == str):
            fval = [gc(v) for v in val]
        else:
            fval = val

        os.environ[get_session_id() + name] = str(fval)
        st.toast(f"Update {name} to {fval}", icon="⚙️")
    except Exception as e:
        st.error(f"{name} {e}")


Variable.update_cookie = update_cookie


def get_var_input(key, **kwargs):
    v = variables[key]
    input_format = getattr(st, v.input_format) if v.input_format else st.number_input
    return v.get_input(input_format, **kwargs)


def get_value(key):
    return variables[key].get_init_value(session_id=session_id)


def get_inputs(vars, options=[], rvals={}):
    for p, col in enumerate(st.columns(len(vars))):
        with col:
            kwargs = options[p] if len(options) > p else {}
            rvals[vars[p]] = get_var_input(vars[p], **kwargs)
    return rvals


def get_temperature_menu(race_choice):
    col1, col2, col3 = st.columns(3)
    with col1:
        atemp = get_var_input(f"temperature_menu_{race_choice}")
        is_manual_temp = gc(atemp) == "temp_manual"
        is_date_temp = gc(atemp) == "temp_from_date"
    with col2:
        temperature = get_var_input(f"temperature_{race_choice}", disabled=not is_manual_temp)
    with col3:
        get_var_input(f"dtemperature_{race_choice}", disabled=not is_date_temp)
    return temperature


def get_temperature(race_choice):
    return (
        None
        if get_value(f"temperature_menu_{race_choice}") == "temp_auto"
        else get_value(f"temperature_{race_choice}")
    )
