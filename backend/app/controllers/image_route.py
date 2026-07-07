import json
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
async def upload_image(
        file: UploadFile = File(...),
        exif_data: Optional[str] = Form(None)):

    # Validation: Ensuring the user actually uploaded an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code = HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image (PNG, HEIC, JPEG, etc.)."
        )

    try:
        client_metadata = None
        if exif_data:
            try:
                client_metadata = json.loads(exif_data)
            except json.JSONDecodeError:
                print("Warning: Could not decode incoming client-side exif_data string.")

        #READ: Reading the file by grabbing raw binary data
        image_bytes = await file.read()
        new_processor = ImageProcessor(image_bytes, client_metadata=client_metadata)
        lat, lon, heading, bearing, unix_time = new_processor.run()

        planeIdentifer = IdentifyPlane(lat, lon, heading, bearing, unix_time)
        lePlane, laPlanes=  planeIdentifer.planeRanker()


        return lePlane

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occured while processing the image: {str(e)} "
        )



