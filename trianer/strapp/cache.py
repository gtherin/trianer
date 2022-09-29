import datetime

import streamlit as st
import extra_streamlit_components as stx

from ..core.variable import Variable
from ..core.labels import *


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


class Cache:
    cookie_manager = get_manager()


def get_key(key):
    return "trianer_" + key


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

        Cache.cookie_manager.set(get_key(name), fval, expires_at=datetime.datetime(year=2023, month=2, day=2))
    except Exception as e:
        pass
        # st.error(f"{key} {fval}")
        # st.error(e)


Variable.update_cookie = update_cookie


def init_cache_manager(key="trianer_app"):

    with st.empty():
        Variable.cookies = Cache.cookie_manager.get_all(key=key)

    return Cache.cookie_manager, Variable.cookies


init_cache_manager(key="trianer_cache")
