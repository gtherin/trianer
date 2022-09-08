from .diver import Diver


def get_nery():
    return Diver(
        {
            # Description
            "name": "Guillaume Néry",
            "body mass": 78,  # in kg
            "gas volume": 9,  # in l
            # Material
            "thickness suite": 1.5,  # in mm
            "ballast mass": 1,  # in kg
            # Performance
            "final depth": 125,  # in m
            "descent_time": 120,  # in sec
            # SHOULD BE DEPRECATED
            "descet speed": 125 / 120.0,  # in m/sec
            # SHOULD BE DEPRECATED
            "ascent speed": 125 / 94.0,  # in m/sec
            "ascent_time": 94,  # in sec
            "descent eq. depth": 27.5,  # in m
            "error descent eq. depth": 2.5,  # in m
            "ascent eq. depth": 7.5,  # in m
            "error ascent eq. depth": 2.5,  # in m
            "comment": """
- la profondeur maximale: 125m
- la vitesse moyenne: 3'34" Aller retour. Aller en 2'00 et retour en 1'34"
- la profondeur à laquelle l'apnéiste se laisse glisser vers le bas: Je me laisse glisser entre 25 et 30 metres mais au cours de la chute de la chute libre, j'effectue à 3 reprises un petit coup de palme pour donner un peu plus de vitesse (à environ 35-40m puis 50-55m et enfin aux environ des 65m
- la profondeur à laquelle l'apnéiste se laisse glisser vers le haut. Je me laisse glisser vers le haut les 5 -10 derniers metres seulement.
- le volume total des poumons (capacité vitale + volume résiduel) . Ma capacité vitale avec carpe change selon les années mais est environ à 9litres. Aucune idée de mon volume résiduel donc pas d'info sur ma capacité totale non plus.
- le poids de l'apnéiste (corps et lest) Je pèse 78kg, je porte une combinaison de 1,5mm et un plomb de cou de 1kg.
    """,
        }
    )


def get_tourreau():

    return Diver(
        {
            # Description
            "name": "Stephane Tourreau",
            "body mass": 71,  # in kg
            "gas volume": 8,  # in l
            "thickness suite": 3,  # in mm
            "ballast mass": 1.5,  # in kg
            "final depth": 103,  # in m
            "descet speed": 103 / (2 * 60 + 45) * 2,  # in m/min
            "ascent speed": 103 / (2 * 60 + 45) * 2,  # in m/min
            "descent eq. depth": 55,  # in m
            "error descent eq. depth": 5,  # in m
            "ascent eq. depth": 10,  # in m
            "error ascent eq. depth": 2.5,  # in m
        }
    )
