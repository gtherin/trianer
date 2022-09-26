import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import glob

import streamlit as st
import hydralit_components as hc
import extra_streamlit_components as stx
from streamlit_folium import folium_static

import trianer
import trianer.st_inputs as tsti
from trianer.labels import gl, set_language

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


trianer.set_var_on_change_function(update_cookie)
trianer.set_var_cookies(all_cookies)


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    return trianer.Race.load_races_configs()


def get_pars(pars):
    return {"name" if k in ["race_format", "race_default"] else k: tsti.get_value(k) for k in pars}


def main():

    # set_language(tsti.get_value("language"))

    # specify the primary menu definition
    menu_data = [
        {"id": "athlete", "icon": "💗"},
        {"id": "race", "icon": "🌍"},
        {"id": "perf", "icon": "🏊🚴🏃"},
        {"id": "simulation", "icon": "🏆"},
        # {"id": "about", "icon": "💻"},
    ]
    menu_steps = [m["id"] for m in menu_data]
    for m in menu_data:
        m["label"] = gl(m["id"])

    over_theme = {"txc_inactive": "#FFFFFF"}

    use_nav_bar = False
    if use_nav_bar:
        menu_id = hc.nav_bar(
            menu_definition=menu_data,
            override_theme=over_theme,
            hide_streamlit_markers=False,
            sticky_nav=True,
            sticky_mode="pinned",
        )
    else:
        menu_id = stx.stepper_bar(steps=menu_steps)

    if menu_id == "perf" or menu_id == menu_steps.index("perf"):
        st.header(gl(menu_id))
        tsti.get_inputs(["swimming_sX100m", "cycling_kmXh", "running_sXkm"])
        tsti.get_inputs(["transition_swi2cyc_s", "transition_cyc2run_s"])

    # with tab2:
    if menu_id == "race" or menu_id == menu_steps.index("race"):
        race_menu = tsti.get_value("race_menu")
        if race_menu == gl("existing_race"):
            race_title = trianer.Race(tsti.get_value("race_default")).get_info()
        elif race_menu == gl("existing_format"):
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
            race_title = trianer.Race.init_from_cookies(tsti.get_value).get_info()

        st.header(f"{race_title}")
        # st.success(f"Race info: {race.get_info()} (code={race.get_key()})")

        race_menu = tsti.get_var_input("race_menu")
        if race_menu == gl("existing_race"):
            tsti.get_var_input("race_default")
            tsti.get_temperature_menu("race")
        elif race_menu == gl("existing_format"):
            tsti.get_inputs(["race_format", "cycling_dplus", "running_dplus"])
            tsti.get_temperature_menu("format")
        else:
            # if st.file_uploader("") is None:
            #    st.write("Or use sample dataset to try the application")

            disciplines = tsti.get_var_input("disciplines")
            c, noc = 0, int(np.sum([1 if d == "swimming" else 2 for d in disciplines]))
            cols = st.columns(noc)
            for d in disciplines:
                with cols[c]:
                    tsti.get_var_input(f"{d}_lengh")
                c += 1
                with cols[c]:
                    if d in ["cycling", "running"]:
                        tsti.get_var_input(f"p{d}_dplus")
                        c += 1

            tsti.get_temperature_menu("perso")

    # with tab3:
    if menu_id == "athlete" or menu_id == menu_steps.index("athlete"):
        st.header(gl(menu_id))
        tsti.get_inputs(["sex", "weight_kg", "height_cm"])
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #    tsti.get_var_input("language", disabled=True)

        tsti.get_inputs(["language", "year_of_birth", "sudation"], options=[dict(disabled=True), {}, {}])

    if menu_id == "simulation" or menu_id == menu_steps.index("simulation"):
        st.header(gl(menu_id))

        athlete = trianer.Athlete(
            config=get_pars(
                ["swimming_sX100m", "cycling_kmXh", "running_sXkm"]
                + ["transition_swi2cyc_s", "transition_cyc2run_s", "weight_kg"]
            )
        )

        race_menu = tsti.get_value("race_menu")
        if race_menu == gl("existing_race"):
            race = trianer.Race(name=tsti.get_value("race_default"))
            temperature = tsti.get_temperature("race")
        elif race_menu == gl("existing_format"):
            pars = get_pars(["race_format", "cycling_dplus", "running_dplus"])
            race = trianer.Race(**pars)
            temperature = tsti.get_temperature("format")
        else:
            race = trianer.Race.init_from_cookies(tsti.get_value)
            temperature = tsti.get_temperature("perso")

        # st.success(f"Race info: {race.get_info()} (code={race.get_key()})")
        simulation = trianer.Triathlon(race=race, temperature=temperature, athlete=athlete)

        with st.expander("Summary", expanded=True):
            disciplines = ["Swimming", "Cycling", "Running", "Total"]
            cols = st.columns(4)
            for d, discipline in enumerate(disciplines):
                r = race.get_dinfo(discipline)
                if r[0] > 0:
                    with cols[d]:
                        st.subheader(gl(discipline))

                        st.metric("Distance&D+", f"{r[0]:.2f} km", f"{r[1]:.0f} m", delta_color="off")

            cols = st.columns(4)
            for d, discipline in enumerate(disciplines):
                r = race.get_dinfo(discipline)
                if r[0] > 0:
                    with cols[d]:
                        if discipline != "Total":
                            a = athlete.get_dinfo(discipline)
                            st.metric(
                                "Speed&pace",
                                f"{a[0]:.2f} km/h",
                                f"{a[1]:.0f} s/" + ("km" if discipline.lower() != "swimming" else "100m"),
                                delta_color="off",
                            )

            cols = st.columns(4)
            for d, discipline in enumerate(disciplines):
                r = race.get_dinfo(discipline)
                if r[0] > 0:
                    with cols[d]:
                        if discipline == "Total":
                            du = simulation.data["duration"].sum()
                        else:
                            du = simulation.data.query(f"discipline == '{discipline.lower()}'")["duration"].sum()
                        du = f"{du:.0f}h{60 * (du % 1):02.0f}min"
                        st.metric(
                            "Duration",
                            f"{du}",
                            f"0",
                            delta_color="off",
                        )

        if race_menu == gl("existing_race"):
            with st.expander("Show race gpx track", expanded=False):
                folium_static(simulation.show_gpx_track())

        with st.expander(gl("show_race_details"), expanded=True):
            xaxis = st.radio("x axis", ["Total distance", gl("time_total"), gl("dtime")], horizontal=True, key="moon")
            st.pyplot(simulation.show_race_details(xaxis=xaxis))
            st.pyplot(simulation.show_nutrition(xaxis=xaxis))
        with st.expander("F&B", expanded=True):
            st.markdown(simulation.show_roadmap().to_html(), unsafe_allow_html=True)

    with st.expander(f"ℹ️ - About this app (pyversion={trianer.__version__})", expanded=False):

        # st.header(gl(menu_id))
        vetruve_file = trianer.gpx.get_file("vetruve_gen.png")
        st.image(vetruve_file)
        st.success(f"Using version {trianer.__version__}")
        st.markdown("[Contact Us](mailto:gt@guydegnol.net)")
        st.markdown(open("./CHANGELOG.md", "r").read())

        st.markdown("## Cookies management")
        st.write(all_cookies)
        cookie = st.text_input("Cookie", key="Cookie list")
        if st.button("Delete a cookie"):
            cookie_manager.delete(cookie)


if __name__ == "__main__":
    main()
