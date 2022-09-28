import streamlit as st
from ..race import gpx


def get_expander():
    from ..__version__ import __version__ as version

    return st.expander(f"ℹ️ - About this app (pyversion={version})", expanded=False)


def get_content(all_cookies, cookie_manager):

    from ..__version__ import __version__ as version

    vetruve_file = gpx.get_file("vetruve_gen.png")
    st.image(vetruve_file)
    st.success(f"Version {version}")
    st.markdown(open("./README.md", "r").read())
    st.markdown(open("./CHANGELOG.md", "r").read())

    st.markdown("## Cookies management")
    st.write(all_cookies)
    cookie = st.text_input("Cookie", key="Cookie list")
    if st.button("Delete a cookie"):
        cookie_manager.delete(cookie)


def get_section(all_cookies, cookie_manager):
    with get_expander():
        get_content(all_cookies, cookie_manager)
