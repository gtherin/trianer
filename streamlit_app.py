import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import trianer
import extra_streamlit_components as stx

from streamlit_folium import folium_static
import os


st.set_option("deprecation.showPyplotGlobalUse", False)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
all_cookies = cookie_manager.get_all()


def update_cookie(key):
    val = st.session_state[key]
    fval = str(val) if type(val) == datetime.time else val
    try:
        cookie_manager.set(key, fval, expires_at=datetime.datetime(year=2023, month=2, day=2))
    except Exception as e:
        st.error(f"{key} {fval}")
        st.error(e)


trianer.set_var_on_change_function(update_cookie)
trianer.set_var_cookies(all_cookies)


info_box = st.empty()


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    return trianer.Race.load_races_configs()


races_configs = load_races_configs()


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
    sudation = 5
    hydr.plot(ax=ax)

    st.pyplot(fig)


def get_perso_race():
    race_perso = ""

    pdisciplines = trianer.get_value("disciplines")
    for d in pdisciplines:
        race_perso += f",{d}:" + str(trianer.get_value(f"{d}_lengh"))
        if d in ["cycling", "running"]:
            dplus = trianer.get_value(f"p{d}_dplus")
            race_perso += f":{dplus}"
    return race_perso


def main():

    with st.expander("Athlete's performances", expanded=True):

        col1, col2, col3 = st.columns(3)
        with col1:
            swimming_sX100m = trianer.get_var_slider("swimming_sX100m")

        with col2:
            cycling_kmXh = trianer.get_var_number("cycling_kmXh")

        with col3:
            running_sXkm = trianer.get_var_slider("running_sXkm")

        col1, col2 = st.columns(2)
        with col1:
            transition_swi2cyc_s = trianer.get_var_slider("transition_swi2cyc_s")

        with col2:
            transition_cyc2run_s = trianer.get_var_slider("transition_cyc2run_s")

    race_menu = trianer.get_value("race_menu")
    if race_menu == "Existing race":
        race_title = trianer.Race(trianer.get_value("race_default")).get_info()
    elif race_menu == "Existing format":
        race_title = trianer.Race(trianer.get_value("race_format")).get_info()
    else:
        race_title = trianer.Race(get_perso_race()).get_info()

    with st.expander(race_title, expanded=True):
        race_menu = trianer.get_var_radio("race_menu")
        available_races = [r for r in list(races_configs.keys()) if "Info" not in r]
        trianer.variables["race_default"].srange = available_races
        if race_menu == "Existing race":
            temperature = None
            race_default = trianer.get_var_selectbox("race_default")
        elif race_menu == "Existing format":
            col1, col2, col3 = st.columns(3)
            with col1:
                race_format = trianer.get_var_selectbox("race_format")
            with col2:
                cycling_dplus = trianer.get_var_number("cycling_dplus")
            with col3:
                running_dplus = trianer.get_var_number("running_dplus")
        else:
            st.warning("Shoud be implemented soon")
            if st.file_uploader("") is None:
                st.write("Or use sample dataset to try the application")
                # sample = st.checkbox("Download sample data from GitHub")

            disciplines = trianer.get_var_multiselect("disciplines")
            c, noc = 0, int(np.sum([1 if d == "swimming" else 2 for d in disciplines]))
            cols = st.columns(noc)
            dlongueur = []

            race_perso = ""

            for d in disciplines:
                with cols[c]:
                    if "swimming" == d:
                        swimming_lengh = trianer.get_var_number("swimming_lengh")
                        dlongueur.append(swimming_lengh)
                    if "cycling" == d:
                        cycling_lengh = trianer.get_var_number("cycling_lengh")
                        dlongueur.append(cycling_lengh)
                    if "running" == d:
                        running_lengh = trianer.get_var_number("running_lengh")
                        dlongueur.append(running_lengh)
                race_perso += f",{d}:{dlongueur[-1]}"
                c += 1
                with cols[c]:
                    if "cycling" == d:
                        pcycling_dplus = trianer.get_var_number(f"p{d}_dplus")
                        race_perso += f":{pcycling_dplus}"
                        c += 1
                    if "running" == d:
                        prunning_dplus = trianer.get_var_number(f"p{d}_dplus")
                        race_perso += f":{prunning_dplus}"
                        c += 1

        col1, col2, col3 = st.columns(3)
        with col1:
            atemp = st.radio("Temperature", ["Manual", "From date"])
        with col2:
            temperature = trianer.get_var_number("temperature", disabled=(atemp != "Manual"))
        with col3:
            dtemperature = trianer.get_var_date("dtemperature", disabled=(atemp == "Manual"))

    with st.expander("Athlete's details", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            weight_kg = trianer.get_var_number("weight_kg")
        with col2:
            year_of_birth = trianer.get_var_number("year_of_birth")
        with col3:
            height_cm = trianer.get_var_number("height_cm")

    athlete = trianer.Athlete(
        name="John Doe",
        config=dict(
            swimming_sX100m=swimming_sX100m,
            cycling_kmXh=cycling_kmXh,
            running_sXkm=running_sXkm,
            transition_swi2cyc_s=transition_swi2cyc_s,
            transition_cyc2run_s=transition_cyc2run_s,
            weight_kg=weight_kg,
        ),
    )

    if race_menu == "Existing race":
        race = trianer.Race(epreuve=race_default)
    elif race_menu == "Existing format":
        race = trianer.Race(epreuve=race_format, cycling_dplus=cycling_dplus, running_dplus=running_dplus)
    else:
        race = trianer.Race(epreuve=race_perso)
        # race = trianer.Race(longueur=dlongueur, disciplines=disciplines, cycling_dplus=cycling_dplus, running_dplus=running_dplus)

    st.write(race.get_info())
    ttemperature = temperature if atemp == "Manual" else 34

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

    with st.expander("Cookies management", expanded=False):
        st.write(all_cookies)
        st.write(
            dict(
                swimming_sX100m=swimming_sX100m,
                cycling_kmXh=cycling_kmXh,
                running_sXkm=running_sXkm,
                transition_swi2cyc_s=transition_swi2cyc_s,
                transition_cyc2run_s=transition_cyc2run_s,
                weight_kg=weight_kg,
            )
        )
        cookie = st.text_input("Cookie", key="2")
        if st.button("Delete"):
            cookie_manager.delete(cookie)

    # st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")
    # st.sidebar.selectbox("Epreuve", races_names, key="krace_name")


if __name__ == "__main__":
    main()
