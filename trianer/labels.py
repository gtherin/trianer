class Labels:
    labels = {
        # Menus
        "perf": ["Performances", "Performances"],
        "race": ["Race details", "Details course"],
        "athlete": ["Athlete details", "Details Athlete"],
        "simulation": ["Race simulation", "Simulation"],
        "about": ["About", "A propos"],
        "show_race_details": ["Show race details", "Details de la course"],
        "existing_race": ["Existing race", "Course existante"],
        "existing_format": ["Existing format", "Format predefini"],
        "personalized_format": ["Personalized format", "Format personalisé"],
        "favorite_language": ["Favorite language", "Language préféré"],
        # Variables
        "cduration_min": ["Since start", "Depuis depart"],
        "dtime_str": ["Transit time", "Temps de passage"],
        "hydric_balance": ["Hydric balance", "Bilan hydrique"],
        "caloric_balance": ["Caloric balance", "Bilan calorique"],
        "time_total": ["Total time", "Durée totale"],
        "Food supply": "Alimentation",
        "fdistance": ["Total distance (km)", "Distance totale(km)"],
        "dtime": ["Time of day", "Heure de la journée"],
        "etime": ["Time since start", "Temps depuis le départ"],
        "caloric_reserve": ["Caloric reserve (kcal)", "Reservoir energetique (kcal)"],
        "hydration_ideal": ["With perfect hydration (ml)", "Avec une hydratation ideale (ml)"],
        "risk_zone": ["Risk zone", "Zone de risque"],
        "perf_loss_20": ["Performance loss (20%)", "Perte de perf (20%)"],
    }

    language_idx = 0


def set_language(language):
    Labels.language_idx = 1 if language == "Fr" else 0


def gl(name):
    if name in Labels.labels.keys():
        l = Labels.labels[name]
        return l[Labels.language_idx] if type(l) == list else l

    return name
