import os

import trianer


def test_gpx():
    trianer.race.gpx.clean_file("tests/Barden.gpx", [], debug=True)
    # trianer.race.gpx.clean_files(filename="tests/anon_gpx.json")


if __name__ == "__main__":
    test_gpx()
