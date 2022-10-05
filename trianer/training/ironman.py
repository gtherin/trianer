import pandas as pd

# https=//www.kalenji.fr/terminer-mon-premier-marathon-en-12-semaines
# "Marathon (Decathlon, 5h, 12w)"= (

"""
Alternez le footing à allure lente (50 à 75% de la VMA) et le footing à allure rapide (75 à 90% de la VMA) pour progresser.
SEMAINE	Vélo	Course à pied	Natation
"""

program = """1	5H	2H30	3H30
2	4H	2H30	2H30
3	4H30	3H	2H30
4	3H30	2H30	2H30
5	4H30	3H	2H30
6	5H30	3H	3H
7	8H30	3H30	2H30
8	7H	3H30	3H
9	5H30	3H	5H
10	7H30	3H30	3H
11	7H	4H	3H
12	4H	4H30	4H
13	8H	3H30	2H30
14	9H	4H	2H
15	9H30	2H	2H30
16	4H30	5H30	3H30
17	8H30	3H30	4H
18	6H	3H30	2H30
19	6H	3H	3H
20	30 min	1H	1H30
""".replace(
    "H", "h"
).replace(
    "	", ","
)

ironman = pd.DataFrame(
    [row.split(",") for row in program.split("\n")], columns=["week", "cycling", "running", "cycling"]
)
