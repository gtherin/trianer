import streamlit as st
from ..race import gpx
import os

from ..core.labels import gl, gc, Labels
from . import inputs


def get_expander():
    from ..__version__ import __version__ as version

    return st.expander(f"ℹ️ - {gl('about_app')} (pyversion={version})", expanded=False)


def get_content():
    from ..__version__ import __version__ as version

    st.image(gpx.get_file("vetruve_gen.png"))
    st.success(f"Version {version}")
    rd = open("./README.md", "r").read()
    st.markdown(rd)

    cl = open("./CHANGELOG.md", "r").read().split("[")
    st.markdown("[".join(cl[:3]))
    if st.checkbox("More changes history"):
        st.markdown("#### [" + "[".join(cl[3:]))

    st.subheader("Parameters")
    st.write({k: v for k, v in os.environ.items() if "TRAINER" in k})

    if inputs.get_var_input("beta_mode"):
        st.success(Labels.add_label(en="Beta mode is activated !", fr="Le mode beta est activé !"))


def get_section():
    with get_expander():
        get_content()
