import os

import trianer

# python -d pytest tests


def test_gpx_raw():
    trianer.race.gpx_formatter.GpxFormatter.clean_file(
        "tests/Barden.gpx", [], debug=True
    )
    print("AAAAAAAAAAAAaa")
    # trianer.race.gpx_formatter.clean_files(filename="tests/anon_gpx.json")
    with open("tests/Barden_HR.gpx", "r") as f:
        lines = f.readlines()
        print(lines[:10])


def test_gpx_kiki():
    trianer.race.gpx_formatter.GpxFormatter.clean_files(
        filters={
            "tests/A Maniccia.gpx": [
                {
                    "min_time": "09:20:05",
                    "max_time": "13:59:18",
                    "altitude_offset": {"min": 0, "max": 20},
                },
                {
                    "min_time": "14:20:05",
                    "max_time": "18:59:18",
                    "altitude_offset": {"min": 20, "max": 0},
                },
            ]
        },
        debug=True,
        remove_time=True,
    )
    return
    print("AAAAAAAAAAAAaa")
    # trianer.race.gpx_formatter.clean_files(filename="tests/anon_gpx.json")
    with open("tests/A Maniccia_HR.gpx", "r") as f:
        lines = f.readlines()
        print(lines[:10])


def test_gpx_mc():
    trianer.race.gpx_formatter.GpxFormatter.clean_file(
        "tests/Monte Cinto.gpx", [], debug=True
    )


def test_gpx_gt():
    trianer.race.gpx_formatter.GpxFormatter.clean_file(
        "tests/Gorges du Tavignano.gpx", [], debug=True
    )


def test_dd_toy():
    import pandas as pd

    d = pd.Series([1] * 20 + [-1] * 10 + [1] * 40).cumsum()

    dds = [trianer.race.gpx_formatter.Dd(band=band) for band in [0, 1, 2, 3, 5]]

    for a in d:
        for dd in dds:
            dd.update(a)

    for dd in dds:
        dd.print()


# python -m pytest tests/test_gpx.py -k test_gpx_raw -s
# python tests/test_gpx.py
if __name__ == "__main__":
    test_gpx_mc()
