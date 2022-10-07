# "Marathon (Schneider, 4h00)"= (
marathon_4h = (
    [
        "l=w1",
        "a=w,t=h5+4x(t=7m30,d=1.5km+t=h2,v=a0)+t=h15,v=a1",
        "t=1h30,v=a2+a=g,t=10m+a=t,t=10m",
        "a=w,t=h5+15x(t=20s,hr=100+t=20s,v=a0)+t=15m,v=a1",  # Cote moderé
        "t=30m,v=a2+4x(t=10m,a=5m41+t=3m,v=a0)+t=11m,v=a1",  # Cote moderé
    ]
    + [
        "l=w2",
        "a=w,t=h5+t=h18,d=3km+2x(t=10m42s,d=2km+t=h2,v=a0)+t=h15,v=a1",
        # Should prepare for the D+, check D+ of race
        "a=w,t=h5+6x(t=30s,hr=100+t=10s,v=a0)+t=h3,v=a0+6x(t=30s,hr=100+t=10s,v=a0)+t=h15,v=a1",  # Cote moderé
        "t=1h45,v=a2",
    ]
    + [
        "l=w3",
        "a=w,t=h5+7x(t=5m40s,d=1km+t=1m45s,v=a0)+t=1h,v=a1",
        # Should prepare for the D+, check D+ of race
        "a=w,t=h5+10x(t=40s,hr=100+t=10s,v=a0)+t=h15,v=a1",  # Cote moderé
        "t=2h,v=a2",
    ]
    + [
        "l=w4",
        "a=w,t=h5+3x(t=h12,d=2km+t=h3,v=a0)+t=h15,v=a1",
        "a=w,t=h5+4x(p=10-20-30)+t=h15,v=a1",  # Cote moderé
        "t=1h45,v=a2",
    ]
    + [
        "l=w5",
        "a=w,t=h5+t=h30,d=5km+t=h2,v=a0+t=11m40s,d=2km+t=h5,v=a0+t=5m25s,d=1km+t=h15,v=a1",
        "t=h30,v=a2",
        "a=w,t=h12+t=2h08,d=21km,v=a2",
    ]
    + [
        "l=w6",
        "t=1h15,v=a2",
        "a=w,t=h5+7x(t=4m30s,d=0.8km+t=h2,v=a0)+t=h15,v=a1",
        "t=2h10,v=a2",
    ]
    + [
        "l=w7",
        "a=w,t=h5+2x(t=17m45s,d=3km+d=0.4,v=a0)+t=h15,v=a1",
        "a=w,t=h5+8x(t=2m25s,d=0.5km+t=1m15s,v=a0)+t=h15,v=a1",
        "t=2h20,v=a2",
    ]
    + [
        "l=w8",
        "a=w,t=h5+2x(t=h23,d=4km+d=0.4,v=a0)+t=h15,v=a1",
        "a=w,t=h5+8x(t=3m18s,d=0.6km+d=0.2,v=a0)+t=h15,v=a1",
        "t=2h,v=a2",
    ]
    + [
        "l=w9",
        "t=h30,v=a2+t=30m50s,d=5km+t=h10,v=a2",
        "a=w,t=h5+6x(t=2m28s,d=0.5km+t=1m10s,v=a0)",
        "t=1h20,v=a2",
    ]
    + ["l=w10", "t=20m,v=a2+t=12m20s,d=2km+t=h10,v=a1", "t=20m,v=a2+a=t,t=10m", "a=r"]
)
