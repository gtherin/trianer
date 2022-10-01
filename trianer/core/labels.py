class Label:
    def __init__(self, key="dummy", en=None, fr=None, units=False, hen=None, hfr=None) -> None:
        self.key, self.units = key, units
        self.en = self.key if not en else en
        self.fr = self.en if not fr else fr
        self.hen, self.hfr = hen, hen if not hfr else hfr


class Labels:
    labels = {
        # Menus
        0: ["Athlete", "Athlete"],
        "athlete": ["Athlete", "Athlete"],
        1: ["Race", "Course"],
        "race": ["Race", "Course"],
        2: ["Performances", "Performances"],
        "perf": ["Performances", "Performances"],
        3: ["Simulation", "Simulation"],
        "simulation": ["Simulation", "Simulation"],
        4: ["Training", "Entrainement"],
        "training": ["Training", "Entrainement"],
        "about": ["About", "A propos"],
        "about_app": ["About this app", "A propos de l'appli"],
        "race_menu": ["Type of race", "Format de course"],
        "temp_auto": ["Automatic", "Automatique"],
        "temp_manual": ["Manual", "Manuel"],
        "temp_from_date": ["From date", "A partir d'une date"],
        # Athlete
        "sex": ["Sex", "Sexe"],
        "year_of_birth": ["Year of birth", "Année de naissance"],
        "male": ["Male", "Homme"],
        "female": ["Female", "Femme"],
        "sudation": ["Sudation", "Sudation"],
        "existing_race": ["Existing race", "Course existante"],
        "existing_format": ["Existing format", "Format predefini"],
        "personalized_format": ["Personalized format", "Format personalisé"],
        "language": ["Favorite language", "Langage préféré"],
        "weight_kg": ["Weight (kg)", "Poids (kg)"],
        "height_cm": ["Height (cm)", "Taille (cm)"],
        # Performances
        "swimming_sX100m": ["Swimming pace (min:sec/100m)", "Allure de nage (min:sec/100m)"],
        "cycling_kmXh": ["Cycling speed (km/h)", "Vitesse cyclisme (km/h)"],
        "running_sXkm": ["Running pace (min:sec/km)", "Allure de course (min:sec/km)"],
        "transition_swi2cyc_s": ["Transition time swi./cyc. (min:sec)", "Temps de transition nat./cyc. (min:sec)"],
        "transition_cyc2run_s": ["Transition time cyc./run. (min:sec)", "Temps de transition cyc./cou. (min:sec)"],
        # Race
        "slope": ["Slope", "Pente"],
        "speed": ["Speed", "Vitesse"],
        "swimming": ["Swimming", "Natation"],
        "cycling": ["Cycling", "Cyclisme"],
        "running": ["Running", "Course"],
        "pcycling_dplus": ["Positive elevation gain cyc. (m)", "D+ cyclisme (m)"],
        "prunning_dplus": ["Positive elevation gain run. (m)", "D+ course (m)"],
        "race_format": ["Race format", "Format de course"],
        "temperature": ["Temperature", "Temperature"],
        "temperature_menu_race": ["Temperature", "Temperature"],
        "temperature_menu_perso": ["Temperature", "Temperature"],
        "temperature_menu_format": ["Temperature", "Temperature"],
        # Variables
        "hydric_balance": ["Hydric balance", "Bilan hydrique"],
        "caloric_balance": ["Caloric balance", "Bilan calorique"],
        "time_total": ["Total time", "Durée totale"],
        "fdistance": ["Total distance", "Distance totale"],
        "dtime": ["Time of day", "Heure de la journée"],
        "etime": ["Time since start", "Temps depuis le départ"],
        "caloric_reserve": ["Caloric reserve", "Reservoir energetique"],  # (kcal)
        "hydration_ideal": ["With perfect hydration", "Avec une hydratation ideale"],  # (ml)
        "risk_zone": ["Risk zone", "Zone de risque"],
        "perf_loss_20": ["Performance loss (20%)", "Perte de perf (20%)"],
        "altitude": ["Altitude", "Altitude"],
    }

    units = {
        "caloric_reserve": "kcal",
        "hydration_ideal": "ml",
        "hydric_balance": "ml",
        "caloric_balance": "kcal",
        "altitude": "m",
        "temperature": "°C",
        "temperature_menu_race": "°C",
        "temperature_menu_perso": "°C",
        "temperature_menu_format": "°C",
        "fdistance": "km",
        # Race
        "slope": "Percent",
        "speed": "km/h",
    }

    language_idx = 0
    codes = None

    @staticmethod
    def add_label(*kargs, **kwargs):
        label = Label(*kargs, **kwargs)
        Labels.labels[label.key] = [label.en, label.fr]
        Labels.codes[0][label.en] = label.key
        Labels.codes[1][label.fr] = label.key
        if label.units:
            Labels.units[label.key] = label.units
        return gl(label.key, u=label.units)


Labels.codes = [{v[0]: k for k, v in Labels.labels.items()}, {v[1]: k for k, v in Labels.labels.items()}]


def set_language(language):
    Labels.language_idx = 1 if language == "Fr" else 0


def gl(name, u=False):
    if name not in Labels.labels.keys():
        return name

    l = Labels.labels[name][Labels.language_idx]
    return l + units(name) if u else l


def gc(name):
    for l in [0, 1]:
        if name in Labels.codes[l]:
            return Labels.codes[l][name]

    return name


def translate(name):
    if name in Labels.codes[Labels.language_idx]:
        return name
    code = gc(name)
    return gl(code)


def units(name):
    if name in Labels.units.keys():
        return " (" + Labels.units[name] + ")"

    return ""
