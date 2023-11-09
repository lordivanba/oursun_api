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
from dto.kitDeleteImageDto import KitDeleteImageDto
from dto.kitUpdateRequestDto import KitUpdateRequestDto
from dto.respond import Respond

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
        return ApiResponseDto(
            success=False,
            data=None,
            message="kits not found",
        )

    return ApiResponseDto(
        success=True,
        data=kits,
        message="message",
    )


@router.get("/get_kit_By_Id/{kit_id}", dependencies=[Depends(JWTBearer())])
async def get_kits_by_Id(kit_id: str):
    doc_ref = db.collection("kits").document(kit_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Kit not found")
    kit = doc.to_dict()
    kit["id"] = doc.id

    # Convert the kit to a kit object.
    dto_kit = Kit(**kit)
    value = dto_kit.model_dump()
    return Respond(
        success=True,
        data=value,
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


@router.post("/upload", dependencies=[Depends(JWTBearer())])
async def upload_kit(data: KitCreateRequestDto):
    kit = Kit(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        features=data.features,
        price=data.price,
        images=None,
    )
    # Guarda el objeto "kit" en Firestore, si es necesario
    response_data = kit.model_dump()
    doc_ref = db.collection("kits").document(kit.id).set(response_data)

    return Respond(
        success=True,
        data={"id": kit.id},
        message="Kit created successfully.",
    )


@router.put("/upload_Images/{user_id}", dependencies=[Depends(JWTBearer())])
async def upload_images(user_id, images: List[UploadFile] = File(...)):
    doc_ref = db.collection("kits").document(user_id)

    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Kit not found")

    for image_file in images:
        if not allowed_file(image_file.filename):
            raise HTTPException(
                status_code=422, detail="Only JPG, JPEG, and PNG files are allowed."
            )
    image_urls = doc.get("images")

    try:
        for image_file in images:
            image_url = processImage(image_file)
            image_urls.append(image_url)

        data = {"images": image_urls}
        doc_ref.update(data)

        return Respond(
            success=True, data=None, message="The images Has Been Updated Succesfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_kit/{kit_id}", dependencies=[Depends(JWTBearer())])
def update_kit(user_id: str, request: KitUpdateRequestDto):
    doc_ref = db.collection("kits").document(user_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the document with the new data.
    data = {
        "name": request.name,
        "description": request.description,
        "features": request.features,
        "price": request.price,
    }
    doc_ref.update(data)
    # Return a success message.
    return Respond(
        success=True, data=None, message="The kit has been successfully updated"
    )


@router.delete("/delete/{kit_id}", dependencies=[Depends(JWTBearer())])
def kit_delete(kit_id: str):
    doc_ref = db.collection("kits").document(kit_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="kit not found")

    doc_ref.delete()

    # Return the respond
    return Respond(
        success=True, data=None, message="The kit Has Been deleted Successfully"
    )


@router.delete("/delete_image", dependencies=[Depends(JWTBearer())])
def kit_delete_image(data: KitDeleteImageDto):  
    #Searching for the specific kit with the id
    doc_ref = db.collection("kits").document(data.id)

    # Check if the document exists
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Kit not found")

    # Save images_urls in a variable called images
    images = doc.get("images")
    
    #Validate if the kit has images
    if not images:
        raise HTTPException(status_code=422, detail="No images found for the kit")
    
    #Search the specific image in the array
    for i, image in enumerate(images):
        if image == data.image_url:
            break
    else:
        raise HTTPException(
            status_code=422, detail="The image URL does not match the images"
        )
    
    #Delete the selected image
    del images[i]
    
    #Update firebase images
    doc_ref.update({"images": images })

    return Respond(success=True, data=None, message="The image has been deleted succesfully")


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
