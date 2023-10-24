import io
import uuid
from auth.jwt_bearer import JWTBearer
from dto.api_response_dto import ApiResponseDto
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from firebase_admin import firestore, storage
from PIL import Image


router = APIRouter()

# Initialize Firebase Storage
storage_client = storage.bucket("our-sun-30a0c.appspot.com")
db = firestore.client()


@router.post("/upload/", dependencies=[Depends(JWTBearer())])
async def upload_image(image: UploadFile = File(...)):
    if not allowed_file(image.filename):
        raise HTTPException(
            status_code=422, detail="Only JPG, JPEG, and PNG files are allowed."
        )

    try:
        image_url = processImage(image)

        return ApiResponseDto(
            success=True,
            data=[{"url": image_url}],
            message="Image uploaded and user created successfully.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_first_image_url", dependencies=[Depends(JWTBearer())])
async def get_first_image_url():
    # List all objects in the root

    blobs = storage_client.list_blobs()

    # Find the first image (you may want to implement your own logic here)
    first_image = None
    for blob in blobs:
        blob.make_public()
        if blob.content_type.startswith("image/"):
            first_image = blob
            break

    if first_image:
        # Get the public URL of the image
        public_url = first_image.public_url
        return {"image_url": public_url}
    else:
        return {"error": "No images found in Firebase Storage"}


def processImage(image: UploadFile = File(...)):
    optimized_image = optimize_image(image.file, image.content_type)

    image_url = saveImageInStorage(optimized_image, image.content_type)

    return image_url


def saveImageInStorage(image, content_type):
    # Save the image to Firebase Storage with the correct content type\
    myuuid = uuid.uuid4()
    blob = storage_client.blob(str(myuuid))
    blob.upload_from_file(image, content_type=content_type)
    image_url = blob.public_url
    blob.make_public()
    return image_url


def optimize_image(file, filename):
    # Open the image using PIL
    img = Image.open(file)

    # Determine the format of the image (convert it to lowercase for comparison)
    image_format = filename.split(".")[-1].lower()

    # Resize and compress the image
    img = img.resize((int(img.width / 2), int(img.height / 2)))

    img = img.convert("RGB")  # Convert to RGB mode

    img_byte_array = io.BytesIO()

    if image_format in ["jpeg", "jpg"]:
        img.save(img_byte_array, format="JPEG", quality=70)
    elif image_format == "png":
        print("its PNG!")
        img.save(img_byte_array, format="PNG", optimize=True)
    else:
        # For unsupported formats, default to JPEG with a lower quality
        img.save(img_byte_array, format="JPEG", quality=70)

    img_byte_array.seek(0)

    return img_byte_array


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
