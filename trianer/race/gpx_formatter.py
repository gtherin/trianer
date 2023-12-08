import datetime
import os
import json
import logging


def get_default_datetime():
    return datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)


class Point:
    @staticmethod
    def get_anchor_value(point, anchor):
        return point[
            point.find(f"<{anchor}>") + len(f"<{anchor}>") : point.find(f"</{anchor}>")
        ]

    @staticmethod
    def get_latitude(point):
        for p in point.split():
            if "lat=" in p:
                return float(p[5:-2])

    @staticmethod
    def get_longitude(point):
        for p in point.split():
            if "lon=" in p:
                return float(p[5:-2])

    @staticmethod
    def get_altitude(point):
        if "ele" in point:
            # WARNING: numpy not available for Francois
            return round(float(Point.get_anchor_value(point, "ele")), 2)
        else:
            return 0.0

    @staticmethod
    def get_time(point):
        if "time" not in point:
            return get_default_datetime()
        ttime = Point.get_anchor_value(point, "time")
        return datetime.datetime.strptime(ttime[:19], "%Y-%m-%dT%H:%M:%S")

    def update_altitude(self, altitude):
        if not self.is_valid_gpx:
            return

        point = self.npoint
        self.npoint = (
            point[: point.find("<ele>") + len("<ele>")]
            + "%.2f" % altitude
            + point[point.find("</ele>") :]
        )

    def delete_tag(self, tag):
        if not self.is_valid_gpx or tag not in self.npoint:
            return
        point = self.npoint
        self.npoint = (
            point[: point.find(tag)]
            + point[point.find(tag.replace("<", "</")) + len(tag) + 1 :]
        )

    def __init__(self, point, splitter="<trkpt", remove_time=True, debug=False):
        self.is_valid_gpx = "lat=" in point
        self.is_valid_tcx = "<AltitudeMeters>" in point

        self.point = point
        self.latitude = -1
        self.longitude = -1
        self.altitude = -1
        self.distance = -1
        self.dtime = get_default_datetime()
        self.temperature = -1
        self.hr = -1
        self.remove_time = remove_time
        self.debug = debug

        if self.is_valid_gpx:
            self.point = splitter + point
            self.latitude = self.get_latitude(self.point)
            self.longitude = self.get_longitude(self.point)
            self.altitude = self.get_altitude(self.point)
            self.dtime = self.get_time(self.point)
            if "gpxtpx:atemp" in point:
                self.temperature = Point.get_anchor_value(self.point, "gpxtpx:atemp")
            if "ns3:atemp" in point:
                self.temperature = Point.get_anchor_value(self.point, "ns3:atemp")
            if "gpxtpx:hr" in point:
                self.hr = Point.get_anchor_value(self.point, "gpxtpx:hr")
            if "ns3:hr" in point:
                self.hr = Point.get_anchor_value(self.point, "ns3:hr")
        elif self.is_valid_tcx:
            self.point = splitter + point
            self.latitude = Point.get_anchor_value(self.point, "LatitudeDegrees")
            self.longitude = Point.get_anchor_value(self.point, "LongitudeDegrees")
            self.altitude = Point.get_anchor_value(self.point, "AltitudeMeters")
            self.dtime = Point.get_anchor_value(self.point, "Time")
            self.distance = Point.get_anchor_value(self.point, "DistanceMeters")
        self.npoint = self.point

    def get_formatted_point(self, debug=False):
        self.npoint = self.npoint.replace("\n", "").replace("\t", " ")
        if self.is_valid_gpx and debug:
            print(self.npoint)
        return self.npoint + "\n"


def get_diff_in_seconds(time1, time2):
    return (
        datetime.datetime.combine(datetime.date.today(), time1)
        - datetime.datetime.combine(datetime.date.today(), time2)
    ).seconds


class GpxFormatter:
    def __init__(self, filename, creator="GPS Track Editor"):
        self.filename = filename
        self.xml = None
        self.filecontent = ""
        self.ddo, self.dup, self.palt = 0, 0, -999

        if self.exists():
            xml = open(self.filename, "r").read()
            xml = xml.replace(creator, "https://www.horizonrando.fr")
            self.xml = xml.split("<trkpt")

    def exists(self):
        return os.path.exists(self.filename)

    def apply_filter(self, point, filter):
        ctime = point.dtime.time()

        altitude_offset = 0
        if ctime >= filter["min_time"] and ctime <= filter["max_time"]:
            if type(filter["altitude_offset"]) == dict:
                altitude_global_offset = (
                    filter["altitude_offset"]["max"] - filter["altitude_offset"]["min"]
                )

                altitude_offset = altitude_global_offset * (
                    get_diff_in_seconds(ctime, filter["min_time"]) / filter["diff_time"]
                )
                altitude_offset += filter["altitude_offset"]["min"]

            else:
                altitude_offset = filter["altitude_offset"]

            print(
                "%s: Altitude %s offset to %sm"
                % (self.filename, point.dtime.time(), int(altitude_offset))
            )
            point.altitude += altitude_offset
        return point

    def save(self):
        with open(self.filename.replace(".gpx", "_HR.gpx"), "w") as f:
            f.write(self.filecontent)

    def update_filecontent(self, p, filters, remove_time=True, debug=False):
        point = Point(p)
        for filter in filters:
            point = self.apply_filter(point, filter)

        if not point.is_valid_gpx:
            self.filecontent += point.npoint
            return point.npoint

        point.delete_tag("<extensions>")
        if remove_time:
            point.delete_tag("<time>")

        # S'il n'y a pas d'extensions : (et commenter ligne au dessus
        point.update_altitude(point.altitude)
        if self.palt == -999:
            self.palt = point.altitude
        dalt = point.altitude - self.palt
        if dalt > 0:
            self.dup += dalt
        else:
            self.ddo += dalt

        self.palt = point.altitude

        self.filecontent += point.get_formatted_point(debug=debug)

    @staticmethod
    def clean_file(
        filename, filters, remove_time=True, debug=False, creator="GPS Track Editor"
    ):
        gpx_file = GpxFormatter(filename, creator=creator)

        if not gpx_file.exists():
            print(f"{filename}: File does not exist")
            return

        for d, p in enumerate(gpx_file.xml):
            gpx_file.update_filecontent(
                p, filters, remove_time=remove_time, debug=debug and d < 10
            )

        print(f"Denivelé total: d+={gpx_file.dup:.0f}m d-={-gpx_file.ddo:.0f}m")
        gpx_file.save()

    @staticmethod
    def clean_files(filename="gpx.json", filters=None, debug=False, remove_time=True):
        if filters is None:
            filters = json.load(open(filename, "r"))

        for filename, filters in filters.items():
            for filter in filters:
                filter["min_time"] = datetime.datetime.strptime(
                    filter["min_time"], "%H:%M:%S"
                ).time()
                filter["max_time"] = datetime.datetime.strptime(
                    filter["max_time"], "%H:%M:%S"
                ).time()
                filter["diff_time"] = get_diff_in_seconds(
                    filter["max_time"], filter["min_time"]
                )

            GpxFormatter.clean_file(
                filename, filters, debug=debug, remove_time=remove_time
            )


if __name__ == "__main__":
    GpxFormatter.clean_files()
