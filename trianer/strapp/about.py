import streamlit as st
from ..race import gpx

from ..core.labels import gl, gc, Labels
from . import inputs


def get_expander():
    from ..__version__ import __version__ as version

    return st.expander(f"ℹ️ - {gl('about_app')} (pyversion={version})", expanded=False)


def get_content(all_cookies, cookie_manager):

    from ..__version__ import __version__ as version

    vetruve_file = gpx.get_file("vetruve_gen.png")
    st.image(vetruve_file)
    st.success(f"Version {version}")
    st.markdown(open("./README.md", "r").read())

    cl = open("./CHANGELOG.md", "r").read().split("[")
    st.markdown("[".join(cl[:3]))
    if st.checkbox("More changes history"):
        st.markdown("#### [" + "[".join(cl[3:]))

    if st.checkbox("Cookies management"):
        st.write(all_cookies)
        cookie = st.text_input("Cookie", key="Cookie list")
        if st.button("Delete a cookie"):
            cookie_manager.delete(cookie)

    if inputs.get_var_input("beta_mode"):
        st.success(Labels.add_label(en="Beta mode is activated !", fr="Le mode beta est activé !"))


def get_section(all_cookies, cookie_manager):
    with get_expander():
        get_content(all_cookies, cookie_manager)
