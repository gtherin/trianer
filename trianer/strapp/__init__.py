import os


def push():
    logs = open("CHANGELOG.md", "r").read().split("####")
    for l in logs:
        if "TODO" not in l and "[" in l:
            break

    comments = [f"-m '{c[2:]}'" for i, c in enumerate(l.split("\n")) if i > 1 and c != ""]
    comments = " ".join(comments)
    cmd = f"trianer-vetruve && git add . && git commit {comments} && git push heroku master"
    print(cmd)
    os.system(cmd)


from . import about
from . import cache
from .menu import Menu
from .metrics import show_metrics
from .getters import get_athlete, get_race, get_temperature
from . import research
