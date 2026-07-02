from fastapi import APIRouter, File, UploadFile, HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST
from backend.app.services.image_processor import ImageProcessor
from backend.app.services.plane_identifier import IdentifyPlane

router = APIRouter (
    prefix="/images",
    tags=["Images"]
)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Controller endpoint to accept an image upload.
    """

    # Validation: Ensuring the user actually uploaded an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code = HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image (PNG, HEIC, JPEG, etc.)."
        )

    try:
        #READ: Reading the file by grabbing raw binary data
        image_bytes = await file.read()
        new_processor = ImageProcessor(image_bytes)
        lat, lon, heading, bearing, unix_time = new_processor.run()

        planeIdentifer = IdentifyPlane(lat, lon, heading, bearing, unix_time)
        lePlane, laPlanes=  planeIdentifer.planeRanker()






        # 3. CALL THE SERVICE (Model Layer) - Placeholder for now
        # TODO: api_response = external_api.query(metadata)

        #TemporaRY mock response to prove the controller works
        vital = {
            "latitude": lat,
            "longitude": lon,
            "heading": heading,
            "camera_bearing_ref": bearing

        }

        return lePlane

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occured while processing the image: {str(e)} "
        )



