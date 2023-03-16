import os

import trianer


def test_gpx():
    trianer.race.gpx_formatter.GpxFormatter.clean_file("tests/Barden.gpx", [], debug=True)
    # trianer.race.gpx_formatter.clean_files(filename="tests/anon_gpx.json")


def test_gpx2():
    trianer.race.gpx_formatter.GpxFormatter.clean_files(
        filters={
            "tests/A Maniccia.gpx": [
                {"min_time": "09:20:05", "max_time": "13:59:18", "altitude_offset": {"min": 0, "max": 20}},
                {"min_time": "14:20:05", "max_time": "18:59:18", "altitude_offset": {"min": 20, "max": 0}},
            ]
        },
        debug=True,
        remove_time=True,
    )


if __name__ == "__main__":
    test_gpx2()