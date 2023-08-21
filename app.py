import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import os
import uuid
import datetime
import random


logo_file = os.path.abspath(os.path.dirname(__file__) + f"/data/trianer_v3.png")

st.set_page_config(
    page_title="Trianer",
    page_icon=Image.open(logo_file),  # ":running:"
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": open("./README.md", "r").read(),
    },
)
st.set_option("deprecation.showPyplotGlobalUse", False)


import trianer
from trianer import strapp

import trianer.strapp.inputs as tsti

from trianer.core.labels import gl, gc, set_language

from trianer.core.variables import load_default_data

default_data = load_default_data()


class RaceConfig(strapp.PersistentSettings):
    BATCH_SIZE: int = 10
    EPOCHS: int = 10
    EARLY_STOPPING: int = 5

    def parameter_block(self):
        self.BATCH_SIZE = int(st.number_input("Batch Size", 1, 1024, int(self.BATCH_SIZE)))

        self.EPOCHS = int(st.number_input("Epochs", 1, 10 * 1000, int(self.EPOCHS)))

        self.EARLY_STOPPING = int(
            st.number_input("Eearly Stopping - Patience in epochs", 1, 10 * 1000, int(self.EARLY_STOPPING))
        )


class PerformanceConfig(strapp.PersistentSettings):
    BATCH_SIZE: int = 10
    EPOCHS: int = 10
    EARLY_STOPPING: int = 5

    def parameter_block(self):
        self.BATCH_SIZE = int(st.number_input("Batch Size", 1, 1024, int(self.BATCH_SIZE)))

        self.EPOCHS = int(st.number_input("Epochs", 1, 10 * 1000, int(self.EPOCHS)))

        self.EARLY_STOPPING = int(
            st.number_input("Eearly Stopping - Patience in epochs", 1, 10 * 1000, int(self.EARLY_STOPPING))
        )


def main():
    set_language(tsti.get_value("language"))
    menu = strapp.Menu(beta_mode=tsti.get_value("beta_mode"))

    configs = {"athlete": strapp.AthleteMenu(), "race": RaceConfig(), "perf": PerformanceConfig()}

    if menu.is_menu(menu_id := "athlete"):
        configs[menu_id].parameter_block()
        if st.button(f"Submit {menu_id} changes", key=f"{menu_id}_update"):
            configs[menu_id].update()
            st.toast(f"Your {menu_id} parameters was saved!", icon="😍")
    if menu.is_menu(menu_id := "race"):
        configs[menu_id].parameter_block()
        if st.button(f"Submit {menu_id} changes", key=f"{menu_id}_update"):
            configs[menu_id].update()
            st.toast(f"Your {menu_id} parameters was saved!", icon="😍")
    if menu.is_menu(menu_id := "perf"):
        configs[menu_id].parameter_block()
        if st.button(f"Submit {menu_id} changes", key=f"{menu_id}_update"):
            configs[menu_id].update()
            st.toast(f"Your {menu_id} parameters was saved!", icon="😍")

    if menu.is_menu(menu_id := "simulation"):
        st.subheader(gl(menu_id))

    st.write(configs)


if __name__ == "__main__":
    main()
