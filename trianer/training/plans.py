"""

hr=80 course rapide
hr=70-75 course normale
hr=65-70 aisance respiratoire, peux parler pendant la course
hr=50 is slow run, trotinant


10-20-30
4 séries de 5 min d’entraînement 10-20-30 avec 2 minutes de récupération entre les séries.
Mesure vitesse au 100 metres
Les 10 secondes à >90% de la vitesse maximale (vitesse déterminée par une épreuve de sprint de 100 m), 
les 20 secondes à 60% de la vitesse maximale 
les 30 secondes à 30% de la vitesse maximale.


t=duration
d=distance
hr=heart rate
v=vitesse
a=activity
  a=s swimming
  a=c cycling
  a=r running

  a=w warmup
  a=g gainage
  a=t stretching

  a= fractionné
  += running D+
  -= running D-

p=specific program
  10-20-30
    """
# Be able to link
# allure max versus duration
# Vo2 max versus speed

from .marathon_5h import marathon_5h
from .marathon_4h30 import marathon_4h30
from .marathon_4h import marathon_4h
from .ironman import ironman

plans = {"5h": marathon_5h, "4h30": marathon_4h30, "4h": marathon_4h, "ironman": ironman}


allures = {
    "2h45": "3m54",
    "3h": "4m15",
    "3h15": "4m37",
    "3h30": "4m58",
    "3h45": "5m19",
    "4h": "5m41",
    "4h15": "6m02",
    "4h30": "6m23",
    "4h45": "6m45",
    "5h": "7m06",
}

"""
5h
a0 = 9m00 au km
a1 = 8m20
a2 = 7m06
am = 7m06 # allure marathon

4h30
a0 = 8m30 au km
a1 = 7m30 = 8m05-6m50 au km
a2 = 6m23 = 6m50-5m55 au km
am = 6m23 # allure marathon

4h00
a0 = 8m00 au km
a1 = 6m55 = 7m31-6m22 au km
a2 = 5m41 = 6m22-5m20 au km
am = 5m41 # allure marathon
"""

allures1 = {"5h": "8m20", "4h30": "7m30", "4h00": "6m55"}
allures0 = {"5h": "9m00", "4h30": "8m30", "4h00": "8m00"}


import datetime


def get_time_min(val):
    def g(n):
        return 0 if n == "" else int(n.replace("s", "").replace("m", ""))

    h, m, s = "", "", ""
    if "h" in val:
        h, m = val.split("h")
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(s))
    elif "m" in val:
        m, s = val.split("m")
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(s))
    else:
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(val))


class Plan:
    def __init__(self, ttime, vo2max=50) -> None:
        self.plan = plans[ttime]
        self.ttime = ttime
        vo2max = vo2max
        self.paces = {"a0": allures0[ttime], "a1": allures1[ttime], "a2": allures[ttime], "am": allures[ttime]}


# https=//www.schneiderelectricparismarathon.com/fr/se-preparer/plan-guides
# https=//www.timeto.com/Assets/TimeTo/plans/marathon_3h00
# https=//www.timeto.com/Assets/TimeTo/plans/marathon_4h00
