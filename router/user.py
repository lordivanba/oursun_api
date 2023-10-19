from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Union
import uuid

# ----------------------------------------------------------------
from dto.requestUpdateUserDto import RequestUpdateUserDto
from dto.requestUserDto import RequestUserDto
from dto.respondUpateUserDto import RespondUpdateUserDto
from dto.respondUserAuthorized import RespondUserAuthorized
from dto.respondUserDto import DtoUser

# ----------------------------------------------------------------
from models.user import User, UserLoginSchema
from models.respond import RespondUser

# ----------------------------------------------------------------
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

# ----------------------------------------------------------------
from auth.jwt_handler import signJWT
from auth.jwt_bearer import JWTBearer

# ----------------------------------------------------------------

user = APIRouter()


# ----------------------------------------------------------------

# Use a service account.
cred = credentials.Certificate("our-sun-30a0c-firebase-adminsdk-l1nr7-e5d1d542bb.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()


def get_db():
    return db


# ----------------------------------------------------------------
# Método de obtención de Token mediante JWT


@user.post("/signup")
async def create_user(
    request: RequestUserDto,
    db: firestore.Client = Depends(get_db),
):
    user = User(
        id=str(uuid.uuid4()),
        isAuthorized=False,
        origin=request.origin,
        type=request.type,
        username=request.username,
        email=request.email,
        user_password=request.user_password,
    )

    try:
        doc_ref = db.collection("users").document(user.id).set(user.model_dump())
        # RespondUser(success=True, data=[], message="The user has been created successfully")
        return signJWT(user.email)
    except Exception as e:
        return RespondUser(success=False, data=str(e), message="")


@user.post("/login")
def user_login(user: UserLoginSchema = Body(default=None)):
    if check_user(user):
        return RespondUser(
            success=True,
            data=[signJWT(user.email)],
            message="The User Loged Succesfully",
        )
    else:
        raise HTTPException(status_code=404, detail= "User not Found")


def search_email(email):
    collection = db.collection("users")
    doc_ref = collection.where("email", "==", email).get()
    doc = doc_ref[0] if doc_ref else None
    return doc if doc is not None else None


def search_password(password):
    collection = db.collection("users")
    doc_ref = collection.where("user_password", "==", password).get()
    doc = doc_ref[0] if doc_ref else None

    return doc if doc is not None else None


def check_user(data: UserLoginSchema):
    email = search_email(data.email)
    password = search_password(data.password)

    if email is None or password is None:
        return False

    email_value = email.get("email")
    password_value = password.get("user_password")

    if data.email == email_value and data.password == password_value:
        return True
    else:
        return False


# ----------------------------------------------------------------


# Metodos Get User
@user.get("/get_users", dependencies=[Depends(JWTBearer())])
def get_users(db: firestore.Client = Depends(get_db)):
    docs = db.collection("users").get()

    users = []
    for doc in docs:
        user = doc.to_dict()
        user["id"] = doc.id

        # Convert the user to a DtoUser object.
        dto_user = DtoUser(**user)

        users.append(dto_user)

    if not users:
        return RespondUser(success=False, data=[{"message": "No users found"}])

    return RespondUser(success=True, data=users, message="")


@user.get("/get_byId/{user_id}", dependencies=[Depends(JWTBearer())])
async def get_by_Id(user_id: str, db: firestore.Client = Depends(get_db)):
    users_ref = db.collection("users").document(user_id)

    # Get the document with the specified ID.
    doc = users_ref.get()

    # If the document does not exist, raise a 404 error.
    if not doc.exists:
        return RespondUser(success=False, data=[{"message": "User not found"}])

    # Return the document as JSON.
    user = doc.to_dict()
    user["id"] = doc.id

    # Convert the user to a DtoUser object.
    dto_user = DtoUser(**user)

    return RespondUser(success=True, data=[dto_user], message="")


# ----------------------------------------------------------------

# Metodos Post User


# ----------------------------------------------------------------


# Metodos Put User
@user.put("/update/{user_id}", dependencies=[Depends(JWTBearer())])
def update_user(
    user_id: str,
    updated_user: RequestUpdateUserDto,
    db: firestore.Client = Depends(get_db),
):
    doc_ref = db.collection("users").document(user_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the document with the new data.
    data = updated_user.model_dump(exclude_unset=True)
    doc_ref.update(data)

    # Return a success message.
    return RespondUpdateUserDto(
        success=True, message="The User Has Been Updated Succesfully"
    )


# Metodo Put isAuthorized


@user.put(
    "/update_authorized/{user_id}/{isAuthorized}", dependencies=[Depends(JWTBearer())]
)
async def update_user_Is_Authorized(
    user_id: str, isAuthorized: bool, db: firestore.Client = Depends(get_db)
):
    doc_ref = db.collection("users").document(user_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the document with the new data.
    data = {"isAuthorized": isAuthorized}
    doc_ref.update(data)
    # Return a success message.
    return RespondUserAuthorized(
        success=True, message="The User Has Been Updated Succesfully"
    )


# ----------------------------------------------------------------

# Metodos Delete User


@user.delete("/delete/{user_id}", dependencies=[Depends(JWTBearer())])
async def delete_user(user_id: str, db: firestore.Client = Depends(get_db)):
    doc_ref = db.collection("users").document(user_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    doc_ref.delete()

    # Devolver la respuesta
    return RespondUser(
        success=True, data=[], message="The User Has Been deleted Successfully"
    )


# ----------------------------------------------------------------
