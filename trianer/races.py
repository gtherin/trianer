import numpy as np
import datetime

available_races = {
    v["key"]: v
    for v in [
        # Chtriman
        dict(
            key="Nice (Ironman)",
            start_time=datetime.datetime.strptime("2023-06-25 07:30", "%Y-%m-%d %H:%M"),
            distances=[3.8, 180, 42.195],
            dfuelings=[[0], [0, 24, 51, 72, 94, 116, 137, 156], np.arange(0.0, 10.8, 1.8)],
            gpx_data=[",x2", "Nice_XL_cycling.gpx", "Nice_XL_running.gpx,x4"],
        ),
        # Chtriman
        dict(
            key="Chtriman (Ironman)",
            start_time=datetime.datetime.strptime("2023-07-03 07:00", "%Y-%m-%d %H:%M"),
            distances=[3.8, 180, 42.195],
            dfuelings=[[0], [0, 39], [0, 3.25, 6.75]],
            gpx_data=[",x2", "Chtriman_XL_cycling.gpx,x2", "Chtriman_XL_running.gpx,x4"],
        ),
        # Embrunman
        dict(
            key="Embrunman (Ironman)",
            start_time=datetime.datetime.strptime("2023-08-15 06:00", "%Y-%m-%d %H:%M"),
            distances=[3.8, 188, 42.195],
            # dfuelings=[[0], [0, 39], [0, 3.25, 6.75]],
            gpx_data=[",x2", "Embrunman_XL_cycling.gpx", "Embrunman_XL_running.gpx,x3"],
            weather_coordonates=[45.188529, 5.724524],  # Grenoble
        ),
        # Elsassman
        dict(
            key="Elsassman (L)",
            start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M"),
            distances=[1.9, 80.3, 20],
            elevations=[0, 1366, 306],
            # options=["x2", "", "Mx2"],
            dfuelings=[[0], [0, 39], [0, 3.25, 6.75]],
            gpx_data=["Elsassman_L_swimming.gpx,x2", "Elsassman_L_cycling.gpx", "Elsassman_M_running.gpx,x2"],
        ),
        dict(
            key="Elsassman (M)",
            start_time=datetime.datetime.strptime("2022-07-10 11:15", "%Y-%m-%d %H:%M"),
            distances=[1.5, 39.6, 10],
            elevations=[0, 338, 153],
            # options=["x2", "", ""],
            dfuelings=[[0], [0, 20.5], [0, 3.25, 6.75]],
            gpx_data=["Elsassman_M_swimming.gpx,x2", "Elsassman_M_cycling.gpx", "Elsassman_M_running.gpx"],
        ),
        dict(
            key="Elsassman (S)",
            start_time=datetime.datetime.strptime("2022-07-09 10:30", "%Y-%m-%d %H:%M"),
            distances=[0.65, 23.9, 5.2],
            # elevations=[0, 9, 0],
            gpx_data=["Elsassman_S_swimming.gpx", "Elsassman_S_cycling.gpx", "Elsassman_S_running.gpx"],
        ),
        # Deauville
        dict(
            key="Deauville (L)",
            start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M"),
            distances=[1.9, 90, 21.195],
            elevations=[0, 1165, 90],
            # options=["x2", "", "Mx2"],
            dfuelings=[[0], [0, 43], [0, 3, 7]],
            gpx_data=[",x2", "Deauville_L_cycling.gpx", "Deauville_M_running.gpx,x2"],
        ),
        dict(
            key="Deauville (M)",
            start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M"),
            dfuelings=[[0], [0, 20], [0, 3, 7]],
            gpx_data=[",x2", "Deauville_M_cycling.gpx", "Deauville_M_running.gpx,x2"],
        ),
        dict(key="Deauville (S)", start_time=datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M")),
        # Bois-le-Roi
        dict(
            key="Bois-le-Roi (L)",
            start_time=datetime.datetime.strptime("2022-09-10 08:00", "%Y-%m-%d %H:%M"),
            distances=[1.916, 82, 19.8],
            elevations=[0, 472, 132],
            # options=["x2", "", "Mx2"],
            dfuelings=[[0], [0, 43], [0, 3.5, 6.5]],
            gpx_data=["Bois_le_Roi_L_swimming.gpx,x2", "Bois_le_Roi_L_cycling.gpx", "Bois_le_Roi_L_running.gpx,x2"],
        ),
        # Chtriman
        dict(
            key="Paris (Marathon)",
            start_time=datetime.datetime.strptime("2023-04-02 10:00", "%Y-%m-%d %H:%M"),
            distances=[42.195],
            disciplines=["running"],
            dfuelings=[[0, 7, 12.8, 17.7, 22.8, 27, 29.9, 34.6, 38.5]],
            gpx_data=["Paris_Marathon.gpx"],
        ),
        dict(key="Marathon", distances=[42.195], disciplines=["running"], type="format"),
        dict(key="Half-Marathon", distances=[21.195], disciplines=["running"], type="format"),
        dict(key="Ironman", distances=[3.8, 180, 42.195], type="format"),
        dict(key="Half-Ironman (70.3)", distances=[1.9, 90, 21.195], type="format"),
        dict(key="Triathlon (L)", distances=[1.9, 80.0, 20.0], type="format"),
        dict(key="Triathlon (M)", distances=[1.5, 40, 10], type="format"),
        dict(key="Triathlon (S)", distances=[0.65, 20, 5], type="format"),
    ]
}
