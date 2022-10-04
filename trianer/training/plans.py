"""
80= course rapide
70-75= course normale
65-70= aisance respiratoire, peux parler pendant la course
50= is slow run, trotinant


10-20-30
4 séries de 5 min d’entraînement 10-20-30 avec 2 minutes de récupération entre les séries.
Mesure vitesse au 100 metres
Les 10 secondes à >90% de la vitesse maximale (vitesse déterminée par une épreuve de sprint de 100 m), 
les 20 secondes à 60% de la vitesse maximale 
les 30 secondes à 30% de la vitesse maximale.



t=duration
hr=heart rate
d=distance
v=vitesse
a=activity
p=specific program

f=footing

a= fractionné
+= footing montée
-= footing descente
e= echauffement
s= stretching
r=resting

    """
# Be able to link
# allure max versus duration
# Vo2 max versus speed


plans = {
    # https=//www.kalenji.fr/terminer-mon-premier-marathon-en-12-semaines
    "5h": (
        # "Marathon (Decathlon, 5h, 12w)"= (
        ["l=w1", "t=1h,hr=70-75", "t=1h,hr=70-75", "t=1h30,hr=70-75"]
        + ["l=w2", "t=1h,hr=70-75", "t=1h,hr=65-70+t=0h05,hr=80+t=0h10,hr=60", "t=1h45,hr=65-70"]
        + ["l=w3", "t=1h,hr=70-75", "t=0h55,hr=65-70+t=0h10,hr=80+t=0h10,hr=60", "t=2h,hr=65-70"]
        + ["l=w4", "t=0h45,hr=70-75", "a=r", "t=1h,hr=70-75"]  # Rest week
        + ["l=w5", "t=1h30,hr=70-75", "t=h42,hr=65-70+t=0h08,hr=80+t=0h10,hr=60", "t=1h30,hr=65-70"]
        + ["l=w6", "t=1h30,hr=70-75", "t=h30,hr=65-70+t=h8,hr=80+t=h5,v=a0+t=h8,hr=80+t=h9,hr=60", "t=1h30,hr=65-70"]
        + [
            "l=w7",
            "t=1h30,hr=70-75",
            "t=25m,hr=65-70+t=h10,hr=80+t=h5,v=a0+t=h10,hr=80+t=h10,hr=60",
            "t=2h,hr=65-70",
        ]
        + ["l=w8", "t=1h,hr=70-75", "a=r", "t=1h,hr=65-70"]  # Rest week
        + ["l=w9", "t=1h30,hr=70-75", "t=h40,hr=65-70+t=h12,hr=80+t=h8,hr=60", "t=2h15,hr=65-70"]
        + [
            "l=w10",
            "t=h25,hr=65-70+t=h10,hr=80+t=h5,v=a0+t=h10,hr=80+t=h10,hr=60",
            "t=1h15,hr=65-70+t=h5,hr=80+t=h10,hr=60",
            "t=1h30,hr=70-75",
        ]
        + [
            "l=w11",
            "t=1h,hr=70-75",
            "t=h26,hr=65-70+t=h5,hr=100+t=h3,v=a0+t=h5,hr=100+t=h3,v=a0+t=h5,hr=100+t=h3,v=a0+t=h10,hr=60",
            "t=1h30,hr=70-75",
        ]
        + ["l=w12", "t=1h,hr=70-75", "a=r", "a=w,t=h10"]  # Rest week
    ),  # https=//www.timeto.com/Assets/TimeTo/plans/marathon_4h30
    # "Marathon (Schneider, 4h30)"= (
    "4h30": (
        [
            "l=w1",
            "a=e,t=h5+4x(t=8m,d=1.5km+t=h2,v=a0)+t=h15,v=a1",
            # Should prepare for the D+, check D+ of race
            "a=e,t=h5+15x(t=20s,hr=100+t=20s,v=a0)+t=h15,v=a1",  # Cote moderé
            "t=1h30,v=a2",
        ]
        + [
            "l=w2",
            "a=e,t=h5+t=h18,d=3km+2x(t=10m42s,d=2km+t=h2,v=a0)+t=h15,v=a1",
            # Should prepare for the D+, check D+ of race
            "a=e,t=h5+6x(t=30s,hr=100+t=10s,v=a0)+t=h3,v=a0+6x(t=30s,hr=100+t=10s,v=a0)+t=h15,v=a1",  # Cote moderé
            "t=1h45,v=a2",
        ]
        + [
            "l=w3",
            "a=e,t=h5+7x(t=5m40s,d=1km+t=1m45s,v=a0)+t=1h,v=a1",
            # Should prepare for the D+, check D+ of race
            "a=e,t=h5+10x(t=40s,hr=100+t=10s,v=a0)+t=h15,v=a1",  # Cote moderé
            "t=2h,v=a2",
        ]
        + [
            "l=w4",
            "a=e,t=h5+3x(t=h12,d=2km+t=h3,v=a0)+t=h15,v=a1",
            "a=e,t=h5+4x(p=10-20-30)+t=h15,v=a1",  # Cote moderé
            "t=1h45,v=a2",
        ]
        + [
            "l=w5",
            "a=e,t=h5+t=h30,d=5km+t=h2,v=a0+t=11m40s,d=2km+t=h5,v=a0+t=5m25s,d=1km+t=h15,v=a1",
            "t=h30,v=a2",
            "a=e,t=h12+t=2h08,d=21km,v=a2",
        ]
        + [
            "l=w6",
            "t=1h15,v=a2",
            "a=e,t=h5+7x(t=4m30s,d=0.8km+t=h2,v=a0)+t=h15,v=a1",
            "t=2h10,v=a2",
        ]
        + [
            "l=w7",
            "a=e,t=h5+2x(t=17m45s,d=3km+d=0.4,v=a0)+t=h15,v=a1",
            "a=e,t=h5+8x(t=2m25s,d=0.5km+t=1m15s,v=a0)+t=h15,v=a1",
            "t=2h20,v=a2",
        ]
        + [
            "l=w8",
            "a=e,t=h5+2x(t=h23,d=4km+d=0.4,v=a0)+t=h15,v=a1",
            "a=e,t=h5+8x(t=3m18s,d=0.6km+d=0.2,v=a0)+t=h15,v=a1",
            "t=2h,v=a2",
        ]
        + [
            "l=w9",
            "t=h30,v=a2+t=30m50s,d=5km+t=h10,v=a2",
            "a=e,t=h5+6x(t=2m28s,d=0.5km+t=1m10s,v=a0)",
            "t=1h20,v=a2",
        ]
        + ["l=w10", "t=20m,v=a2+t=12m20s,d=2km+t=h10,v=a1", "t=20m,v=a2+a=s,t=10m", "a=r"]
    ),
}

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

    def get_pace(self, format="h:m"):
        return
        # return def get_maxspeed_for_duration(vo2max, duration):
        # return get_relative_intensity(duration) * get_speed_from_vo2max(vo2max)


# https=//www.schneiderelectricparismarathon.com/fr/se-preparer/plan-guides
# https=//www.timeto.com/Assets/TimeTo/plans/marathon_3h00
# https=//www.timeto.com/Assets/TimeTo/plans/marathon_4h00
