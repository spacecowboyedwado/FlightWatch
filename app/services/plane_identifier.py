from main.services.image_processor import ImageProcessor
from main.services.opensky_client import TokenManager
import requests
from geopy import Point
from geopy.distance import distance
from main.config import settings
from io import BytesIO


def findPlane(camera_latitude, camera_longitude, camera_heading, camera_bearing_ref):

    latitude = camera_latitude
    longitude = camera_longitude

    heading = camera_heading
    bearing_ref = camera_bearing_ref

    #Location of camera
    origin = Point(latitude, longitude)

    distance_km = 50
    left_edge_bearing = (heading -15) % 360
    right_edge_bearing = (heading + 15) % 360

    point_left = distance(kilometers=distance_km).destination(origin, left_edge_bearing)
    point_right = distance(kilometers=distance_km).destination(origin, right_edge_bearing)

    lamin = min(origin.latitude, point_left.latitude, point_right.latitude)
    lamax = max(origin.latitude, point_left.latitude, point_right.latitude)
    lomin = min(origin.latitude, point_left.latitude, point_right.latitude)
    lomax = max(origin.latitude, point_left.latitude, point_right.latitude)

    tokens = TokenManager(settings.client_id, settings.client_secret)

    response = requests.get(
        f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}",
        headers=tokens.headers(),
    )

    return response

def planeRanker(responses):
    responses = responses.json()

    filteredPlanes = {}

    if responses["states"] is None:
        print("No planes found.")
        return filteredPlanes

    for stateVector in responses["states"]:

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



