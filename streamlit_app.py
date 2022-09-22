import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

import streamlit as st
import hydralit_components as hc
import extra_streamlit_components as stx
from streamlit_folium import folium_static

import trianer
import trianer.st_inputs as tsti


st.set_option("deprecation.showPyplotGlobalUse", False)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
all_cookies = cookie_manager.get_all()


def update_cookie(key):
    val = st.session_state[key]
    fval = str(val) if type(val) == datetime.time else val
    try:
        cookie_manager.set("trianer_" + key, fval, expires_at=datetime.datetime(year=2023, month=2, day=2))
    except Exception as e:
        st.error(f"{key} {fval}")
        st.error(e)


st.write(st.config.get_option("server.enableCORS"))
trianer.set_var_on_change_function(update_cookie)
trianer.set_var_cookies(all_cookies)


info_box = st.empty()


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    return trianer.Race.load_races_configs()


def configure_physiology():
    st.select_slider(
        "Allure pour la shit",
        options=[f"{m+1}min{s:02.0f}s/100m" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
    )

    st.subheader("Calories")
    st.pyplot(trianer.show_kcalories())

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = trianer.get_kcalories(w, discipline="swimming").set_index("speed")["atl"]
        kcalories.plot(ax=ax)
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = trianer.get_kcalories(w, discipline="running").set_index("speed")["atl"]
        kcalories.plot(ax=ax)
    st.pyplot(fig)

    st.subheader("Hydratation")

    # 1000/1100 kcal pour les hommes et 800/900 kcal par repas

    fig, ax = plt.subplots(figsize=(15, 4))

    temp = np.arange(0, 40)
    hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")
    hydr *= 1.5
    hydr.plot(ax=ax)

    st.pyplot(fig)


def get_pars(pars):
    return {"name" if k in ["race_format", "race_default"] else k: tsti.get_value(k) for k in pars}


def main():

    # specify the primary menu definition
    menu_data = [
        {"id": "perf", "icon": "🏊🚴🏃", "label": "Performances"},
        {"id": "race", "icon": "🌍", "label": "Race details"},
        {"id": "athlete", "icon": "💗", "label": "Athlete details"},
        {"id": "simulation", "icon": "🏆", "label": "Race simulation"},
    ]

    over_theme = {"txc_inactive": "#FFFFFF"}
    menu_id = hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        hide_streamlit_markers=False,
        sticky_nav=True,
        sticky_mode="pinned",
    )

    if menu_id == "perf":
        st.header("Athlete's performances")
        col1, col2, col3 = st.columns(3)
        with col1:
            swimming_sX100m = tsti.get_var_slider("swimming_sX100m")

        with col2:
            cycling_kmXh = tsti.get_var_number("cycling_kmXh")

        with col3:
            running_sXkm = tsti.get_var_slider("running_sXkm")

        col1, col2 = st.columns(2)
        with col1:
            transition_swi2cyc_s = tsti.get_var_slider("transition_swi2cyc_s")

        with col2:
            transition_cyc2run_s = tsti.get_var_slider("transition_cyc2run_s")

    # with tab2:
    if menu_id == "race":
        race_menu = tsti.get_value("race_menu")
        if race_menu == "Existing race":
            race_title = trianer.Race(tsti.get_value("race_default")).get_info()
        elif race_menu == "Existing format":
            race_title = trianer.Race(tsti.get_value("race_format")).get_info()
        else:

            cookies_source = tsti.get_value
            race_perso = ""
            pdisciplines = cookies_source("disciplines")
            for d in pdisciplines:
                race_perso += f",{d}:" + str(cookies_source(f"{d}_lengh"))
                if d in ["cycling", "running"]:
                    dplus = cookies_source(f"p{d}_dplus")
                    race_perso += f":{dplus}"
            st.write(race_perso[1:])
            race_title = trianer.Race.init_from_cookies(tsti.get_value).get_info()

        st.header(f"Race details")
        st.subheader(f"{race_title}")

        race_menu = tsti.get_var_radio("race_menu")
        if race_menu == "Existing race":
            temperature = None
            race_default = tsti.get_var_selectbox("race_default")
        elif race_menu == "Existing format":
            col1, col2, col3 = st.columns(3)
            with col1:
                race_format = tsti.get_var_selectbox("race_format")
            with col2:
                cycling_dplus = tsti.get_var_number("cycling_dplus")
            with col3:
                running_dplus = tsti.get_var_number("running_dplus")
        else:
            # if st.file_uploader("") is None:
            #    st.write("Or use sample dataset to try the application")

            disciplines = tsti.get_var_multiselect("disciplines")
            c, noc = 0, int(np.sum([1 if d == "swimming" else 2 for d in disciplines]))
            cols = st.columns(noc)
            for d in disciplines:
                with cols[c]:
                    tsti.get_var_number(f"{d}_lengh")
                c += 1
                with cols[c]:
                    if d in ["cycling", "running"]:
                        tsti.get_var_number(f"p{d}_dplus")
                        c += 1

            col1, col2, col3 = st.columns(3)
            with col1:
                is_manual_temp = race_menu != "Existing race"
                atemp = st.radio("Temperature", ["Manual", "From date"], index=0, disabled=is_manual_temp)
                is_manual_temp |= atemp == "Manual"
            with col2:
                temperature = tsti.get_var_number("temperature", disabled=not is_manual_temp)
            with col3:
                dtemperature = tsti.get_var_date("dtemperature", disabled=is_manual_temp)

    # with tab3:
    if menu_id == "athlete":
        st.header("Athlete's details")

        with st.expander("Athlete's details", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                sex = tsti.get_var_radio("sex")
            with col2:
                # weight_kg = tsti.get_var_number("weight_kg")
                weight_kg = st.number_input("weight_kg", value=80)
            with col3:
                year_of_birth = tsti.get_var_number("year_of_birth")
            with col4:
                height_cm = tsti.get_var_number("height_cm")

        with st.expander("Cookies management", expanded=False):
            st.write(all_cookies)
            cookie = st.text_input("Cookie", key="2")
            if st.button("Delete"):
                cookie_manager.delete(cookie)

    if menu_id == "simulation":
        st.header("Race simulation")

        athlete = trianer.Athlete(
            config=get_pars(
                ["swimming_sX100m", "cycling_kmXh", "running_sXkm"]
                + ["transition_swi2cyc_s", "transition_cyc2run_s", "weight_kg"]
            )
        )

        race_menu = tsti.get_value("race_menu")
        if race_menu == "Existing race":
            race = trianer.Race(name=tsti.get_value("race_default"))
        elif race_menu == "Existing format":
            pars = get_pars(["race_format", "cycling_dplus", "running_dplus"])
            race = trianer.Race(**pars)
        else:
            race = trianer.Race.init_from_cookies(tsti.get_value)

        st.success(f"Race info: {race.get_info()} (code={race.get_key()})")

        temperature = tsti.get_value("temperature")
        ttemperature = None  # temperature  # if is_manual_temp else None
        simulation = trianer.Triathlon(race=race, temperature=ttemperature, athlete=athlete, info_box=info_box)

        if race_menu == "Existing race":
            with st.expander("Show race gpx track", expanded=False):
                folium_static(simulation.show_gpx_track())

        with st.expander("Show race details", expanded=True):
            xaxis = st.radio("x axis", ["Total distance", "Total time", "Time of day"], horizontal=True)
            st.pyplot(simulation.show_race_details(xaxis=xaxis))
            st.pyplot(simulation.show_nutrition(xaxis=xaxis))
        with st.expander("F&B", expanded=True):
            st.markdown(simulation.show_roadmap().to_html(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
