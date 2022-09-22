import trianer


def test_race():

    print(trianer.Race(name="Nice (Ironman)").get_key())
    print(trianer.Race(name="Elsassman (L)").get_key())
    print(trianer.Race(name="Ironman").get_key())
    print(trianer.Race(name="Triathlon (S)").get_key())
    print(trianer.Race(name="Elsassman (L)").get_info())
    print(trianer.Race(name="Ironman").get_info())
    print(trianer.Race(name="Triathlon (S)").get_info())
