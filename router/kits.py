import fastapi
import io
import uuid

from fastapi.encoders import jsonable_encoder
from auth.jwt_bearer import JWTBearer
from dto.api_response_dto import ApiResponseDto
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from typing import List
from firebase_admin import firestore, storage
from PIL import Image
from dto.kitCreateRequestDto import KitCreateRequestDto

from models.kit import Kit


router = APIRouter()

# Initialize Firebase Storage
storage_client = storage.bucket("our-sun-30a0c.appspot.com")
db = firestore.client()


@router.get("/get_kits", dependencies=[Depends(JWTBearer())])
async def get_kits():
    docs = db.collection("kits").get()
    kits = []

    for doc in docs:
        kit = doc.to_dict()
        kit["id"] = doc.id
        # Convert the kit to a kit object.
        dto_kit = Kit(**kit)
        kits.append(dto_kit)

    if not kits:
        raise HTTPException(status_code=404, detail="Kits not found")

    return ApiResponseDto(
        success=True,
        data=kits,
        message="message",
    )


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


@router.post("/upload")
async def upload_kit(data: KitCreateRequestDto, files: List[UploadFile] = File(...)):
    urls = []
    urls.append(upload_images(files))

    data = Kit(
        id=str(uuid.uuid4()),
        name=data.name,
        price=data.price,
        description=data.description,
        features=data.features,
        images=urls,
    )

    return ApiResponseDto(
        success=True,
        data=data,
        message="Images uploaded and kit created successfully.",
    )


async def upload_images(image: List[UploadFile] = File(...)):
    for image_file in image:
        if not allowed_file(image_file.filename):
            raise HTTPException(
                status_code=422, detail="Only JPG, JPEG, and PNG files are allowed."
            )

    try:
        image_urls = []
        for image_file in image:
            image_url = processImage(image_file)
            image_urls.append(image_url)

        return list(image_urls)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
