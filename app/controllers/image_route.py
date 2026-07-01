from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException
from fastapi.openapi.utils import status_code_ranges
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST
from main.services.image_processor import ImageProcessor
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
        lat, lon, heading, bearing = new_processor.run()



        # 3. CALL THE SERVICE (Model Layer) - Placeholder for now
        # TODO: api_response = external_api.query(metadata)

        #TemporaRY mock response to prove the controller works
        mock_response = {
            "filename": file.filename,
            "content_type": file.content_type,
            "bytes_received": len(image_bytes),
            "status": "Successfully intercepted by the controller!"
        }

        return lat, lon, heading, bearing

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occured while processing the image: {str(e)} "
        )



