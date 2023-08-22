import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import os
import time

# Wait for logo file to be available
while not os.path.exists(logo_file := os.path.abspath(os.path.dirname(__file__) + f"/data/trianer_v3.png")):
    time.sleep(1)

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
from trianer.core.labels import gl, gc, set_language, Labels


def get_menu():
    set_language(tsti.get_value("language"))
    return strapp.Menu(beta_mode=tsti.get_value("beta_mode"))


menu = get_menu()


def main():
    set_language(tsti.get_value("language"))

    if menu.is_menu(menu_id := "athlete"):
        st.subheader(gl(menu_id))
        rvals = tsti.get_inputs(["sex", "weight_kg", "height_cm"])
        rvals = tsti.get_inputs(
            ["language", "year_of_birth", "sudation"], options=[dict(disabled=False), {}, {}], rvals=rvals
        )

    if menu.is_menu(["race", "training"]):
        race_menu = tsti.get_var_input("race_menu")
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

        st.subheader(f"{race_title}")

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

    if menu.is_menu(menu_id := "simulation"):
        st.subheader(gl(menu_id))
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
                Labels.add_label(en="x axis", fr="Axe des x"),
                [gl("fdistance"), gl("time_total"), gl("dtime")],
                horizontal=True,
                key="moon",
            )
            yaxis = st.radio(
                Labels.add_label(en="y axis", fr="Axe des y"),
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

    if menu.is_menu(menu_id := "perf"):
        st.subheader(gl(menu_id))
        tsti.get_inputs(["swimming_sX100m", "cycling_kmXh", "running_sXkm"])
        tsti.get_inputs(["transition_swi2cyc_s", "transition_cyc2run_s"])

    if menu.is_menu(menu_id := "training"):
        st.warning(
            Labels.add_label(
                en=f"⚠️ Section is under construction 🚧",
                fr=f"⚠️ Cette section est cours de construction ",
            )
        )
        race_title = trianer.Race.init_from_cookies(tsti.get_value).get_info()
        race = strapp.get_race()

        tsti.get_inputs(["target_time", "vo2max"])

        target_time = tsti.get_value("target_time")
        h, m = [int(t) for t in str(target_time).split(":")[:2]]
        ttime = f"{h}h{m}" if m != 0 else f"{h}h"

        st.subheader(f"{race_title}")

        athlete = strapp.get_athlete()

        gpace = trianer.training.allures[ttime]
        st.write(f"Marathon in {ttime}: estimated pace {gpace}")

        if ttime in ["4h", "4h30", "5h"]:
            st.pyplot(trianer.training.show_plan(ttime, race=race, athlete=athlete))
        else:
            st.error(f"Training plan not available in {ttime} (estimated pace {gpace})")

        training = trianer.Training(athlete=athlete, race="Marathon", target="4h")
        st.pyplot(training.show_speed_vs_duration())
        st.pyplot(training.show_pace_vs_percentage())

    # Show about section
    if menu.is_menu(["athlete", "simulation", "training"]):
        strapp.about.get_section()

    # Show about section
    if menu.is_menu(["research"]):
        strapp.research.get_section()


if __name__ == "__main__":
    main()
