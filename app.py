import numpy as np
import streamlit as st
from streamlit_folium import folium_static

import trianer
from trianer import strapp

import trianer.strapp.inputs as tsti
from trianer.core.labels import gl, set_language

st.set_option("deprecation.showPyplotGlobalUse", False)
# st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
# st.set_page_config(initial_sidebar_state="collapsed")


# Set up cache
with st.empty():
    cookie_manager = strapp.cache.get_manager()
    all_cookies = cookie_manager.get_all(key="trianer_app")
    strapp.cache.set_var_on_change_function(strapp.cache.update_cookie)
    strapp.cache.set_var_cookies(all_cookies)


def main():

    # set_language(tsti.get_value("language"))
    # set_language(tsti.get_value("language"))
    menu = strapp.Menu()

    if menu.is_menu(menu_id := "perf"):
        st.header(gl(menu_id))
        tsti.get_inputs(["swimming_sX100m", "cycling_kmXh", "running_sXkm"])
        tsti.get_inputs(["transition_swi2cyc_s", "transition_cyc2run_s"])

    if menu.is_menu(menu_id := "race"):
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

    if menu.is_menu(menu_id := "athlete"):
        st.header(gl(menu_id))
        tsti.get_inputs(["sex", "weight_kg", "height_cm"])
        tsti.get_inputs(["language", "year_of_birth", "sudation"], options=[dict(disabled=True), {}, {}])

    if menu.is_menu(menu_id := "simulation"):
        st.header(gl(menu_id))
        race_menu = tsti.get_var_input("race_menu")
        simulation = trianer.Triathlon(
            race=strapp.get_race(), temperature=strapp.get_temperature(), athlete=strapp.get_athlete()
        )

        with st.expander("Summary", expanded=True):
            strapp.show_metrics(simulation)

        if race_menu == gl("existing_race"):
            with st.expander("Show race gpx track", expanded=False):
                folium_static(trianer.show_gpx_track(simulation))

        with st.expander(gl("show_race_details"), expanded=True):
            xaxis = st.radio("x axis", [gl("fdistance"), gl("time_total"), gl("dtime")], horizontal=True, key="moon")
            yaxis = st.radio(
                "y axis",
                [gl("altitude"), gl("fdistance"), gl("speed"), gl("slope")],
                horizontal=True,
                key="ymoon",
            )
            if xaxis != yaxis:
                st.pyplot(simulation.show_race_details(xaxis=xaxis, yaxis=yaxis))
            else:
                st.error(f"x axis ({xaxis}) and y axis ({xaxis}) should not be equal")
            st.pyplot(simulation.show_nutrition(xaxis=xaxis))
        with st.expander("F&B", expanded=True):
            st.markdown(trianer.show_roadmap(simulation).to_html(), unsafe_allow_html=True)

    # Show about section
    if menu.is_menu(["athlete", "simulation"]):
        strapp.about.get_section(all_cookies, cookie_manager)


if __name__ == "__main__":
    main()
