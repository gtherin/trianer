import logging
import os


def get_requests(filename):
    import requests

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    url_req = requests.get(filename)
    url_req.encoding = "UTF-8"

    return url_req


def get_file(filename, read=False):
    if "http" in filename:
        url_req = get_requests(filename)
        if read:
            return url_req.text
        return filename
    else:
        for d in ["./data", "../data"]:
            dfilename = f"{d}/{filename}"
            if os.path.exists(dfilename):
                if read:
                    return open(dfilename, "r").read()
                return dfilename
