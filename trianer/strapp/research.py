import streamlit as st
from ..nutrition import children


def get_section():
    # with st.expander(f"ℹ️ - {gl('about_app')} (pyversion={version})", expanded=False):
    st.pyplot(children.plot_data(in_column=True))
