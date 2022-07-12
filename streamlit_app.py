import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import time

st.set_option("deprecation.showPyplotGlobalUse", False)
st.sidebar.title("Athlete")


poids = st.sidebar.slider(label="Poids (en kg)", min_value=50, max_value=100, value=80)
# epreuve = st.sidebar.slider(label="Poids (en kg)", min_value=50, max_value=100, value=80)

epreuve = st.sidebar.selectbox("Epreuve", ["Elsassman", "Deauville", "Bois"])
longueur = st.sidebar.selectbox("Longueur", ["S", "M", "L"], index=2)

# natation = st.sidebar.slider(label="Poids (en kg)", min_value=50, max_value=100, value=80)
# natation = st.sidebar.selectbox("Longueur", ["S", "M", "L"])


natation = st.sidebar.slider("Allure au 100m", value=time(2, 10), min_value=time(1, 30), max_value=time(3, 0))
transition1 = st.sidebar.slider("Transition 1", value=time(5, 0), min_value=time(1, 0), max_value=time(10, 0))
cyclisme = st.sidebar.slider("Vitesse en km", value=28, min_value=20, max_value=40)
transition2 = st.sidebar.slider("Transition 2", value=time(5, 0), min_value=time(1, 0), max_value=time(10, 0))
course = st.sidebar.slider("Allure au km", value=time(5, 0), min_value=time(3, 0), max_value=time(8, 0))

st.write("Natation ", natation, "min/100m, cyclisme ", cyclisme, " km/h, course ", course, " min/km")

st.title("Performance")

POP_MIN, POP_MAX = st.sidebar.slider(
    "Select the population range (Example: range of age is 0-100)", 0, 10000, (0, 1000)
)


pop_size = st.sidebar.slider(
    label="Choose the Population size ('N') - Creates a population of size 'N' within the population range",
    min_value=1000,
    max_value=20000,
    value=5000,
    step=10,
)


@st.cache
def generate_population():
    np.random.seed(11)
    population = np.random.randint(low=POP_MIN, high=POP_MAX, size=pop_size)
    return population


population = generate_population()
st.sidebar.write(f"(Population mean, std): ({np.round(np.mean(population),2)}, {np.round(np.std(population),2)})")


sample_size = st.sidebar.slider(label="Choose the sample size (n)", min_value=10, max_value=2000, value=100, step=10)

sample_number = st.sidebar.slider(
    label="Choose the number of samples", min_value=10, max_value=2000, value=100, step=10
)


@st.cache
def generate_samples():
    np.random.seed(11)
    sample_index = np.random.randint(low=0, high=len(population), size=(sample_number * sample_size))
    sample = population[sample_index].reshape(sample_number, sample_size)
    sample_means = np.mean(sample, axis=1)
    return sample_means


sample_means = generate_samples()

import trianer

# trianer.Triathlon(epreuve=epreuve, longueur=longueur).show_weather_forecasts()

guillaume = trianer.Triathlon(
    epreuve=epreuve,
    longueur=longueur,
    temperature=[17, 21],
    athlete=trianer.Athlete(
        name="Guillaume",
        poids=poids,
        natation="2min15s/100m",
        cyclisme="25.0km/h",
        course="6min0s/km",
        transitions="10min",
        sudation="faible",
    ),
)


from streamlit_folium import folium_static
import folium

with st.echo():
    folium_static(guillaume.show_gpx_track())
st.pyplot(guillaume.show_race_details())
# st.pyplot(guillaume.show_race_details(xaxis = "itime"))
st.pyplot(guillaume.show_nutrition())
st.write(guillaume.show_roadmap())
