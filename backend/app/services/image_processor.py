from io import BytesIO
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
from fastapi import HTTPException
import time

from starlette import status

register_heif_opener()


class ImageProcessor:
    def __init__(self, image_bytes: bytes, client_metadata=None):
        self.image_file = BytesIO(image_bytes)
        # exifr fields will be directly accessible at the root of this dict
        self.client_metadata = client_metadata or {}

    def serialize_exif_value(self, val):
        """Converts IFDRational and bytes into JSON-serializable types."""
        if hasattr(val, "numerator") and hasattr(val, "denominator"):
            return float(val.numerator) / val.denominator if val.denominator != 0 else 0.0

        if isinstance(val, bytes):
            return val.decode(errors="ignore")

        if isinstance(val, tuple):
            return tuple(self.serialize_exif_value(item) for item in val)

        return val

    def extract_metadata(self):
        self.image_file.seek(0)

        try:
            img = Image.open(self.image_file)
            raw_exif_data = img.getexif()
        except Exception:
            # Fallback check: If the image file wrapper itself fails, but frontend sent valid EXIF data, allow it to bypass
            if self.client_metadata:
                return {}, None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to read the image file format. Please upload a valid image (JPEG, PNG, HEIC)."
            )

        exif_data = {
            ExifTags.TAGS.get(k, k): self.serialize_exif_value(v)
            for k, v in raw_exif_data.items()
        } if raw_exif_data else {}

        return exif_data, raw_exif_data

    def extract_gps(self, raw_exif):
        gps_ifd = raw_exif.get_ifd(34853) if raw_exif else None
        gps_data = {
            ExifTags.GPSTAGS.get(k, k): self.serialize_exif_value(v)
            for k, v in gps_ifd.items()
        } if gps_ifd else {}

        return (
            gps_data.get("GPSLatitude"),
            gps_data.get("GPSLatitudeRef"),
            gps_data.get("GPSLongitude"),
            gps_data.get("GPSLongitudeRef")
        )

    def extract_bearing(self, raw_exif):
        image_direction = None
        image_direction_ref = "T"  # Default reference to True north

        # 1. Attempt binary processing
        if raw_exif:
            gps_ifd = raw_exif.get_ifd(34853)
            gps_data = {
                ExifTags.GPSTAGS.get(k, k): self.serialize_exif_value(v)
                for k, v in gps_ifd.items()
            } if gps_ifd else {}

            image_direction = gps_data.get("GPSImgDirection")
            image_direction_ref = gps_data.get("GPSImgDirectionRef") or "T"

        # 2. Fallback to client-side exifr data
        if image_direction is None:
            image_direction = self.client_metadata.get("GPSImgDirection")
            image_direction_ref = self.client_metadata.get("GPSImgDirectionRef") or "T"

        if image_direction is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No compass heading data found. Make sure your camera's direction/compass tags are enabled."
            )

        return float(image_direction), image_direction_ref

    def extractTime(self):
        exif, exif_data = self.extract_metadata()
        photo_date_time = exif.get("DateTime")

        dt = None

        # 1. Parse standard Pillow format string from binary
        if photo_date_time:
            try:
                dt = datetime.strptime(photo_date_time, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                pass

        # 2. Fallback to exifr's processed timestamp string format (ISO string)
        if not dt:
            # exifr maps creation time to 'DateTimeOriginal' or 'CreateDate'
            client_time = self.client_metadata.get("DateTimeOriginal") or self.client_metadata.get("CreateDate")
            if client_time:
                try:
                    # Clean up trailing Z or millisecond variance if present from JS
                    clean_time = client_time.split(".")[0].replace("Z", "")
                    dt = datetime.fromisoformat(clean_time)
                except ValueError:
                    # Try fallback to your original format if it passed normal EXIF format string
                    try:
                        dt = datetime.strptime(client_time, "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        pass

        if dt:
            unix_timestamp = int(dt.timestamp())
            current_time = int(time.time())
            one_hour_in_seconds = 3600

            if current_time - unix_timestamp > one_hour_in_seconds:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Photo was taken too far in the past. OpenSky tracks flights within the last 60 minutes."
                )

            if unix_timestamp > current_time + 60:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The photo timestamp appears to be set in the future."
                )

            return unix_timestamp

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find creation time metadata in this photo."
        )

    def convert_to_degrees(self, value):
        if not value or len(value) < 3:
            return 0.0
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600)

    def validate_data(self):
        exif_data, raw_exif = self.extract_metadata()

        latitude, latitude_ref, longitude, longitude_ref = self.extract_gps(raw_exif)

        # Check binary processing elements
        binary_gps_valid = all(v is not None for v in [latitude, latitude_ref, longitude, longitude_ref])

        if binary_gps_valid:
            latitude = self.convert_to_degrees(latitude)
            if latitude_ref != "N":
                latitude = -latitude

            longitude = self.convert_to_degrees(longitude)
            if longitude_ref != "E":
                longitude = -longitude

            return latitude, longitude

        # Fallback to pre-calculated decimal values from frontend exifr parser
        client_lat = self.client_metadata.get("latitude")
        client_lon = self.client_metadata.get("longitude")

        if client_lat is not None and client_lon is not None:
            return float(client_lat), float(client_lon)

        # Both binary AND client tracking parameters turned up completely blank
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GPS location coordinates found. Please upload a photo taken with location permissions enabled."
        )

    def run(self):
        exif_data, raw_exif = self.extract_metadata()
        latitude, longitude = self.validate_data()
        camera_heading, camera_bearing_ref = self.extract_bearing(raw_exif)
        unix_time = self.extractTime()

        return latitude, longitude, camera_heading, camera_bearing_ref, unix_time