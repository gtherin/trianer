class Labels:
    labels = {
        # Menus
        "perf": ["Performances", "Performances"],
        2: ["Performances", "Performances"],
        "race": ["Race details", "Details course"],
        1: ["Race details", "Details course"],
        "athlete": ["Athlete details", "Details Athlete"],
        0: ["Athlete details", "Details Athlete"],
        "simulation": ["Race simulation", "Simulation"],
        3: ["Race simulation", "Simulation"],
        "about": ["About", "A propos"],
        "show_race_details": ["Show race details", "Details de la course"],
        "existing_race": ["Existing race", "Course existante"],
        "existing_format": ["Existing format", "Format predefini"],
        "personalized_format": ["Personalized format", "Format personalisé"],
        "favorite_language": ["Favorite language", "Language préféré"],
        # Race
        "slope": ["Slope", "Pente"],
        "speed": ["Speed", "Vitesse"],
        # Variables
        "cduration_min": ["Since start", "Depuis depart"],
        "dtime_str": ["Transit time", "Temps de passage"],
        "hydric_balance": ["Hydric balance", "Bilan hydrique"],
        "caloric_balance": ["Caloric balance", "Bilan calorique"],
        "time_total": ["Total time", "Durée totale"],
        "Food supply": "Alimentation",
        "fdistance": ["Total distance", "Distance totale"],
        "dtime": ["Time of day", "Heure de la journée"],
        "etime": ["Time since start", "Temps depuis le départ"],
        "caloric_reserve": ["Caloric reserve", "Reservoir energetique"],  # (kcal)
        "hydration_ideal": ["With perfect hydration", "Avec une hydratation ideale"],  # (ml)
        "risk_zone": ["Risk zone", "Zone de risque"],
        "perf_loss_20": ["Performance loss (20%)", "Perte de perf (20%)"],
        "temperature": ["Temperature", "Temperature"],
        "altitude": ["Altitude", "Altitude"],
    }

    units = {
        "caloric_reserve": "kcal",
        "hydration_ideal": "ml",
        "hydric_balance": "ml",
        "caloric_balance": "kcal",
        "altitude": "m",
        "altitude": "m",
        "temperature": "°C",
        "fdistance": "km",
        # Race
        "slope": "Percent",
        "speed": "km/h",
    }

    language_idx = 0
    codes = None


Labels.codes = [{v[0]: k for k, v in Labels.labels.items()}, {v[1]: k for k, v in Labels.labels.items()}]


def set_language(language):
    Labels.language_idx = 1 if language == "Fr" else 0
    Labels.codes = {v[Labels.language_idx]: k for k, v in Labels.labels.items()}


def gl(name, u=False):
    if name not in Labels.labels.keys():
        return name

    l = Labels.labels[name][Labels.language_idx]
    return l + units(name) if u else l


def gc(name):
    if name in Labels.codes[Labels.language_idx].keys():
        return Labels.codes[Labels.language_idx][name]

    return name


def units(name):
    if name in Labels.units.keys():
        return " (" + Labels.units[name] + ")"

    return ""
