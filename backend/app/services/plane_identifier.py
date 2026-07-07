from fastapi import HTTPException
from backend.app.services.opensky_client import TokenManager
import requests
from geopy import Point
from geopy.distance import distance
from backend.app.config import settings
import math


class IdentifyPlane:
    def __init__(self,camera_latitude, camera_longitude, camera_heading, camera_bearing_ref, unix_time):
        self.latitude = camera_latitude
        self.longitude = camera_longitude
        self.heading= camera_heading
        self.bearing_ref = camera_bearing_ref
        self.time = unix_time



    def findPlane(self):
        origin = Point(self.latitude, self.longitude)
        distance_km = 50

        point_north = distance(kilometers=distance_km).destination(origin, 0)
        point_south = distance(kilometers=distance_km).destination(origin, 180)

        point_east = distance(kilometers=distance_km).destination(origin, 90)
        point_west = distance(kilometers=distance_km).destination(origin, 270)

        lamin = point_south.latitude
        lamax = point_north.latitude

        lomin = point_west.longitude
        lomax = point_east.longitude


        if lomin > lomax:
            lomin, lomax = lomax, lomin

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
            f"https://opensky-network.org/api/states/all",params=params,
            headers=tokens.headers(),
        )

        response.raise_for_status()

        return response

    def planeRanker(self):
        try:
            responses = self.findPlane()
            data = responses.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error from OpenSky: {e}")
            status_code = e.response.status_code if e.response else 500
            if status_code == 403:
                detail_msg = "OpenSky authentication failed. Please verify API configuration."
            elif status_code == 429:
                detail_msg = "Too many requests sent to OpenSky. Please wait a moment and try again."
            else:
                detail_msg = f"Air traffic tracking service returned an error (HTTP {status_code})."

            raise HTTPException(status_code=400, detail=detail_msg)

        except ValueError:
            print(f"Failed to parse JSON. Response text was: {responses.text}")
            raise HTTPException(
                status_code=502,
                detail="Received an invalid response from the tracking server. Please try again later."
            )

        if data.get("states") is None:
            print("No planes found.")
            raise HTTPException(
                status_code=404,
                detail="No aircraft were detected in your current area at that time."
            )

        camera_coords = (self.latitude, self.longitude)
        planes_with_distances = []
        filteredPlanes = {}


        for stateVector in data["states"]:
            #stateVEctor[7] is baro_altitude
            if (
                stateVector[5] is not None #Longitude
                and stateVector[6] is not None #Latitude
                and stateVector[7] is not None #Baromatic Altitude (metres)
            ):
                plane_id = stateVector[0]
                plane_lat = stateVector[6]
                plane_lon = stateVector[5]
                altitude_metres = stateVector[7]

                lat1 = math.radians(self.latitude)
                lon1 = math.radians(self.longitude)
                lat2 = math.radians(plane_lat)
                lon2 = math.radians(plane_lon)

                delta_lon = lon2 - lon1

                # Formula for bearing from point 1 to point 2
                y = math.sin(delta_lon) * math.cos(lat2)
                x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)

                # Calculate bearing and convert from radians back to degrees (0 to 360)
                bearing_to_plane = (math.degrees(math.atan2(y, x)) + 360) % 360

                angular_difference = abs(bearing_to_plane - self.heading)

                if angular_difference > 180:
                    angular_difference = 360 - angular_difference

                if angular_difference > 15:
                    continue

                filteredPlanes[plane_id] = stateVector


                # Calculating horizontal distance in km
                plane_coords = (plane_lat, plane_lon)
                horizontal_dist_km = distance(
                    camera_coords, plane_coords
                ).km

                # Convert altitude from metres to kilometres
                altitude_km = altitude_metres / 1000.0

                # Calculate 3D straight-line distance (Slant Range)
                # Hypotenuse = sqrt(horizontal^2 + vertical^2)

                true_distance_km = (
                    (horizontal_dist_km**2) + (altitude_km**2)
                ) ** 0.5

                planes_with_distances.append(
                    {"state": stateVector, "distance": true_distance_km}
                )

        if not planes_with_distances:
            print("No planes with valid coordinate data found.")
            raise HTTPException(
                status_code=404,
                detail="Aircraft are in the area, but none match the direction your camera was pointing."
            )

        # Sorting the planes by true 3D distance (closest first)
        planes_with_distances.sort(key=lambda x: x["distance"])
        closest_plane_data = planes_with_distances[0]["state"]

        finalPlane = {
            "icao24": closest_plane_data[0],
            "callsign": (
                closest_plane_data[1].strip() if closest_plane_data[1] else ""
            ),
            "origin_country": closest_plane_data[2],
            "time_position": closest_plane_data[3],
            "last_contact": closest_plane_data[4],
            "longitude": closest_plane_data[5],
            "latitude": closest_plane_data[6],
            "baro_altitude": closest_plane_data[7],
            "on_ground": closest_plane_data[8],
            "velocity": closest_plane_data[9],
            "true_track": closest_plane_data[10],
            "vertical_rate": closest_plane_data[11],
            "sensors": closest_plane_data[12],
            "geo_altitude": closest_plane_data[13],
            "squawk": closest_plane_data[14],
            "spi": closest_plane_data[15],
            "position_source": closest_plane_data[16],
            "calculated_distance_km": planes_with_distances[0]["distance"],
        }

        return finalPlane, filteredPlanes



