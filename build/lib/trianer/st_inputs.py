import streamlit as st

from .variables import variables


def get_var_input(key, **kwargs):
    v = variables[key]
    if v.input_format:
        return v.get_input(getattr(st, v.input_format), **kwargs)

    return v.get_input(st.number_input, **kwargs)


def get_value(key):
    return variables[key].get_init_value()


def get_inputs(vars, options=[]):
    for p, col in enumerate(st.columns(len(vars))):
        with col:
            kwargs = options[p] if len(options) > p else {}
            get_var_input(vars[p], **kwargs)


def get_temperature_menu(race_choice):
    col1, col2, col3 = st.columns(3)
    with col1:
        atemp = get_var_input(f"temperature_menu_{race_choice}")
        is_automatic = atemp == "Automatic"
        is_manual_temp = atemp == "Manual"
    with col2:
        temperature = get_var_input(f"temperature_{race_choice}", disabled=is_automatic or not is_manual_temp)
    with col3:
        get_var_input(f"dtemperature_{race_choice}", disabled=is_automatic or is_manual_temp)
    return temperature


def get_temperature(race_choice):
    return (
        None
        if get_value(f"temperature_menu_{race_choice}") == "Automatic"
        else get_value(f"temperature_{race_choice}")
    )


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

    # 1000/1100 kcal pour les hommes et 800/900 kcal par repas

    fig, ax = plt.subplots(figsize=(15, 4))

    temp = np.arange(0, 40)
    hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")
    hydr *= 1.5
    hydr.plot(ax=ax)

    st.pyplot(fig)
