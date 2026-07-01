from io import BytesIO
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener


register_heif_opener()
class ImageProcessor:
    def __init__(self, image_bytes: bytes):
        self.image_file = BytesIO(image_bytes)

    def serialize_exif_value(self, val):
        """Converts IFDRational and bytes into JSON-serializable types."""
        # Handle IFDRational (and IFDSRational)
        if hasattr(val, "numerator") and hasattr(val, "denominator"):
            return float(val.numerator) / val.denominator if val.denominator != 0 else 0.0

        # Handle binary data (like MakerNote or UserComment) which also crash FastAPI
        if isinstance(val, bytes):
            return val.decode(errors="ignore")

        if isinstance(val, tuple):
            return tuple(self.serialize_exif_value(item) for item in val)

        return val


    def extract_metadata(self):

        self.image_file.seek(0)




        img = Image.open(self.image_file)
        raw_exif_data = img.getexif()

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

        image_latitude = gps_data.get("GPSLatitude")
        image_latitude_ref = gps_data.get("GPSLatitudeRef")

        image_longitude = gps_data.get("GPSLongitude")
        image_longitude_ref = gps_data.get("GPSLongitudeRef")


        return  image_latitude, image_latitude_ref, image_longitude, image_longitude_ref

    def extract_bearing(self, raw_exif):
        gps_ifd = raw_exif.get_ifd(34853) if raw_exif else None

        gps_data = {
                ExifTags.GPSTAGS.get(k, k): self.serialize_exif_value(v)
                for k, v in gps_ifd.items()
            } if gps_ifd else {}

        image_direction = gps_data.get("GPSImgDirection")
        image_direction_ref = gps_data.get("GPSImgDirectionRef")



        return image_direction, image_direction_ref


    def convert_to_degrees(self, value):
        # Converts latitude and longitude from degrees-minutes-seconds to decimal format
        if not value or len(value) < 3:
            return 0.0
        d, m, s = value
        return float(d) + (float(m) / 60.0 ) + (float(s) / 3600)


    def validate_data(self):
        exif_data, raw_exif = self.extract_metadata()

        if not exif_data:
            raise ValueError("No EXIF metadata found")

        latitude, latitude_ref, longitude, longitude_ref = self.extract_gps(raw_exif)

        if None in (latitude, latitude_ref, longitude, longitude_ref):
            raise ValueError("No GPS data found in EXIF metadata")

        latitude = self.convert_to_degrees(latitude)
        if latitude_ref != "N":
            latitude = -latitude

        longitude = self.convert_to_degrees(longitude)
        if longitude_ref != "E":
            longitude = -longitude



        return latitude, longitude

    def run(self):
        exif_data, raw_exif = self.extract_metadata()
        latitude, longitude = self.validate_data()
        camera_heading, camera_bearing_ref = self.extract_bearing(raw_exif)

        leng_data = {
            "latitude": latitude,
            "longitude": longitude,
            "camera_heading": camera_heading,
            "camera_bearing_ref": camera_bearing_ref

        }

        return leng_data






