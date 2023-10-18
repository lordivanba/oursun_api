from fastapi import APIRouter, File, UploadFile, Form
import firebase_admin
from firebase_admin import credentials, firestore, storage

router =  APIRouter()

# Initialize Firebase Admin SDK
# cred = credentials.Certificate("our-sun-30a0c-firebase-adminsdk-l1nr7-e5d1d542bb.json")
# firebase_admin.initialize_app(cred)

# Initialize Firebase Storage
storage_client = storage.bucket("our-sun-30a0c.appspot.com")
db = firestore.client()

@router.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    # Save the image to Firebase Storage
    blob = storage_client.blob(image.filename)
    blob.upload_from_string(image.file.read())
    image_url = blob.public_url
    blob.make_public()
    # Create a new user in Firestore with the image URL
    # user_data = {
    #     "username": username,
    #     "image_url": image_url,
    # }
    # db.collection("users").add(user_data)

    return {"message": "Image uploaded and user created successfully.", "url": image_url}
