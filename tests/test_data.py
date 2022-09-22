import os

import trianer


def test_data():
    for k, v in trianer.available_races.items():
        if "gpx_data" in v:
            for f in v["gpx_data"]:
                filename = f.split(",")[0]
                if filename != "":
                    print(k, filename, os.path.exists(f"./data/{filename}"))
                    if not os.path.exists(f"./data/{filename}"):
                        raise Exception(f"./data/{filename} does not exist")
