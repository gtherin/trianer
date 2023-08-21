import streamlit as st

from ..core.variables import load_default_data
from .persistent_settings import PersistentSettings
from . import inputs as tsti


default_data = load_default_data()


class AthleteMenu(PersistentSettings):
    sex = default_data["sex"].default
    weight_kg = default_data["weight_kg"].default
    height_cm = default_data["height_cm"].default
    language = default_data["language"].default
    year_of_birth = default_data["year_of_birth"].default
    sudation = default_data["sudation"].default

    def parameter_block(self):
        print("AAAAAAAAAAAA", self.dict)
        columns = st.columns(3)
        with columns[0]:
            self.sex = tsti.get_var_input("sex")
        with columns[1]:
            self.weight_kg = tsti.get_var_input("weight_kg")
        with columns[2]:
            self.height_cm = tsti.get_var_input("height_cm")

        columns = st.columns(3)
        with columns[0]:
            self.language = tsti.get_var_input("language", disabled=False)
        with columns[1]:
            self.year_of_birth = tsti.get_var_input("year_of_birth")
        with columns[2]:
            self.sudation = tsti.get_var_input("sudation")

        # tsti.get_inputs(["language", "year_of_birth", "sudation"], options=[dict(disabled=False), {}, {}])
