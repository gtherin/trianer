import datetime

import streamlit as st
import extra_streamlit_components as stx

from ..core.variable import Variable
from ..race.race import Race


st.set_option("deprecation.showPyplotGlobalUse", False)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
all_cookies = cookie_manager.get_all()


def set_var_on_change_function(update_cookie):
    Variable.update_cookie = update_cookie


def set_var_cookies(cookies):
    Variable.cookies = cookies


def update_cookie(key):
    val = st.session_state[key]
    fval = str(val) if type(val) == datetime.time else val
    try:
        cookie_manager.set("trianer_" + key, fval, expires_at=datetime.datetime(year=2023, month=2, day=2))
    except Exception as e:
        pass
        # st.error(f"{key} {fval}")
        # st.error(e)


set_var_on_change_function(update_cookie)
set_var_cookies(all_cookies)


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    return Race.load_races_configs()
