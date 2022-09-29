import numpy as np
import streamlit as st
from streamlit_folium import folium_static

import trianer
from trianer import strapp
from trianer.strapp.cache import Cache

import trianer.strapp.inputs as tsti
from trianer.core.labels import gl, gc, set_language, Labels

st.set_option("deprecation.showPyplotGlobalUse", False)
# st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
# st.set_page_config(initial_sidebar_state="collapsed")


# Get cache
cookie_manager, all_cookies = strapp.cache.init_cache_manager(key="trianer_app")


def main():

    set_language(tsti.get_value("language"))
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
            race_perso = ""
            pdisciplines = tsti.get_value("disciplines")
            for discipline in pdisciplines:
                cd = gc(discipline)
                race_perso += f",{cd}:" + str(tsti.get_value(f"{cd}_lengh"))
                if cd.lower() in ["cycling", "running"]:
                    dplus = tsti.get_value(f"p{cd}_dplus")
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

            Labels.add_label("swimming_lengh", en="Swimming distance", fr="Distance natation", units="km")
            Labels.add_label("cycling_lengh", en="Cycling distance", fr="Distance cyclisme", units="km")
            Labels.add_label("running_lengh", en="Running distance", fr="Distance course", units="km")

            disciplines = tsti.get_var_input("disciplines")
            c, noc = 0, int(np.sum([1 if d == "swimming" else 2 for d in disciplines]))
            cols = st.columns(noc)
            for di in disciplines:
                cd = gc(di)
                with cols[c]:
                    tsti.get_var_input(f"{cd}_lengh")
                c += 1
                with cols[c]:
                    if cd in ["cycling", "running"]:
                        tsti.get_var_input(f"p{cd}_dplus")
                        c += 1

            tsti.get_temperature_menu("perso")

    if menu.is_menu(menu_id := "athlete"):
        st.header(gl(menu_id))
        tsti.get_inputs(["sex", "weight_kg", "height_cm"])
        tsti.get_inputs(["language", "year_of_birth", "sudation"], options=[dict(disabled=False), {}, {}])

    if menu.is_menu(menu_id := "simulation"):
        st.header(gl(menu_id))
        simulation = trianer.Triathlon(
            race=strapp.get_race(), temperature=strapp.get_temperature(), athlete=strapp.get_athlete()
        )

        with st.expander(Labels.add_label(en="Summary", fr="Résumé"), expanded=True):
            strapp.show_metrics(simulation)

        race_menu = tsti.get_value("race_menu")
        if race_menu == gl("existing_race"):
            txt = Labels.add_label(en="Show race gpx track", fr="Voir le tracé gpx")
            with st.expander(txt, expanded=False):
                folium_static(trianer.show_gpx_track(simulation))

        with st.expander(Labels.add_label(en="Show race details", fr="Details de la course"), expanded=True):

            xaxis = st.radio(
                Labels.add_label(en="x axis", fr="Axe x"),
                [gl("fdistance"), gl("time_total"), gl("dtime")],
                horizontal=True,
                key="moon",
            )
            yaxis = st.radio(
                Labels.add_label(en="y axis", fr="Axe y"),
                [gl("altitude"), gl("fdistance"), gl("speed"), gl("slope")],
                horizontal=True,
                key="ymoon",
            )
            if xaxis != yaxis:
                st.pyplot(simulation.show_race_details(xaxis=xaxis, yaxis=yaxis))
            else:
                txt = Labels.add_label(
                    en=f"x axis ({xaxis}) and y axis ({xaxis}) should not be equal",
                    fr=f"Les axes x ({xaxis}) et y ({xaxis}) doivent etre differentes",
                )
                st.error(txt)
            st.pyplot(simulation.show_nutrition(xaxis=xaxis))
        with st.expander(Labels.add_label(en="F&B", fr="Evenements de course"), expanded=True):
            st.markdown(trianer.show_roadmap(simulation).to_html(), unsafe_allow_html=True)

    # Show about section
    if menu.is_menu(["athlete", "simulation"]):
        strapp.about.get_section(all_cookies, cookie_manager)


if __name__ == "__main__":
    main()
