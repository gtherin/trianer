import datetime

races = [
    dict(
        key="Elsassman (L)",
        start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M"),
        distances=[1.9, 80.3, 20],
        elevations=[0, 1366, 306],
        options=["x2", "", "Mx2"],
        dfuelings=[[0], [0, 39], [0, 3.25, 6.75]],
    ),
    dict(
        key="Deauville (L)",
        start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M"),
        distances=[1.9, 90, 21.195],
        elevations=[0, 1165, 90],
        options=["x2", "", "Mx2"],
        dfuelings=[[0], [0, 43], [0, 3, 7]],
    ),
    dict(
        key="Elsassman (M)",
        start_time=datetime.datetime.strptime("2022-07-10 11:15", "%Y-%m-%d %H:%M"),
        distances=[1.5, 39.6, 10],
        elevations=[0, 338, 153],
        options=["x2", "", ""],
        dfuelings=[[0], [0, 20.5], [0, 3.25, 6.75]],
    ),
    dict(
        key="Elsassman (S)",
        start_time=datetime.datetime.strptime("2022-07-09 10:30", "%Y-%m-%d %H:%M"),
        distances=[0.65, 23.9, 5.2],
        elevations=[0, 9, 0],
    ),
    dict(key="Marathon", distances=[42.195], disciplines=["running"]),
    dict(key="Half-Marathon", distances=[21.195], disciplines=["running"]),
    dict(key="Ironman", distances=[3.8, 180, 42.195]),
    dict(key="Half-Ironman", distances=[1.9, 90, 21.195]),
    dict(key="Triathlon (L)", distances=[1.9, 80.0, 20.0]),
    dict(key="Triathlon (M)", distances=[1.5, 40, 10]),
    dict(key="Triathlon (S)", distances=[0.65, 20, 5]),
]

races = {v["key"]: v for v in races}
