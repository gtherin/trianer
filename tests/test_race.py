import trianer


def test_race():

    race = trianer.Race(name="Bois-le-Roi (L)")
    race = trianer.Race(name="Deauville (L)")
    print(trianer.Race(name="Elsassman (L)").get_key())
    print(trianer.Race(name="Nice (Ironman)").get_key())
    race = trianer.Race(name="Embrunman (Ironman)")
    race = trianer.Race(name="Paris (Marathon)")
    race = trianer.Race(name="Paris (M)")

    print(trianer.Race(name="Triathlon (S)").get_info())
    print(trianer.Race(name="Triathlon (L)").get_key())
    print(trianer.Race(name="Ironman").get_key())
    print(trianer.Race(name="Ironman").get_info())
    race = trianer.Race(name="swimming:1.9,cycling:60:600,running:20:100")
    race = trianer.Race(name="swimming:1.9,running:21.195:100")
