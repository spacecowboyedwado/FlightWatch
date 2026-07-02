from backend.app.services.opensky_client import TokenManager
import requests
from geopy import Point
from geopy.distance import distance
from backend.app.config import settings


class IdentifyPlane:
    def __init__(self,camera_latitude, camera_longitude, camera_heading, camera_bearing_ref, unix_time):
        self.latitude = camera_latitude
        self.longitude = camera_longitude
        self.heading= camera_heading
        self.bearing_ref = camera_bearing_ref
        self.time = unix_time



    def findPlane(self):
        #Location of camera
        origin = Point(self.latitude, self.longitude)

        distance_km = 50
        left_edge_bearing = (self.heading -15) % 360
        right_edge_bearing = (self.heading + 15) % 360

        point_left = distance(kilometers=distance_km).destination(origin, left_edge_bearing)
        point_right = distance(kilometers=distance_km).destination(origin, right_edge_bearing)

        lamin = min(origin.latitude, point_left.latitude, point_right.latitude)
        lamax = max(origin.latitude, point_left.latitude, point_right.latitude)

        lomin = min(origin.longitude, point_left.longitude, point_right.longitude)
        lomax = max(origin.longitude, point_left.longitude, point_right.longitude)

        tokens = TokenManager(settings.client_id, settings.client_secret)

        params = {
            "lamin": lamin,
            "lomin": lomin,
            "lamax": lamax,
            "lomax": lomax
        }

        if self.time:
            params["time"] = self.time

        response = requests.get(
            f"https://opensky-network.org/api/states/all?",params=params,
            headers=tokens.headers(),
        )

        return response

    def planeRanker(self):
        responses = self.findPlane()
        data = responses.json()

        filteredPlanes = {}

        if data["states"] is None:
            print("No planes found.")
            return filteredPlanes

        for stateVector in data["states"]:

            if stateVector[7] is not None:
                planeID = stateVector[0]

                filteredPlanes[planeID] = stateVector
        altitudes = []

        if filteredPlanes is not None:
            for icao24, state in filteredPlanes.items():
                altitudes.append(state[7])
                altitudes.sort()

        closestPlane = altitudes[0]

        finalPlane = {}

        for stateVector in responses["states"]:
            if stateVector[7] == closestPlane:
                finalPlane = {
                    "icao24": stateVector[0],
                    "callsign": stateVector[1],
                    "origin_country": stateVector[2],
                    "time_position": stateVector[3],
                    "last_contact": stateVector[4],
                    "longitude": stateVector[5],
                    "latitude": stateVector[6],
                    "baro_altitude": stateVector[7],
                    "on_ground": stateVector[8],
                    "velocity": stateVector[9],
                    "true_track": stateVector[10],
                    "vertical_rate": stateVector[11],
                    "sensors": stateVector[12],
                    "geo_altitude": stateVector[13],
                    "squawk": stateVector[14],
                    "spi": stateVector[15],
                    "position_source": stateVector[16],
                }

        return finalPlane, filteredPlanes



