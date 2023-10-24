from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import Union
import uuid
from dto.api_response_dto import ApiResponseDto

# ----------------------------------------------------------------
from dto.requestUserDto import RequestUserDto
from dto.respondUserDto import DtoUser
from dto.respond import Respond

# ----------------------------------------------------------------
from models.user import User, UserLoginSchema

# ----------------------------------------------------------------
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
from firebase_admin import auth

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
    # Check if the username already exists.
    username_ref = (
        db.collection("users").where("username", "==", request.username).get()
    )
    if username_ref:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(
        id=str(uuid.uuid4()),
        isAuthorized=False,
        origin=request.origin,
        type=request.type,
        username=request.username,
        user_password=request.user_password,
    )

    try:
        doc_ref = db.collection("users").document(user.id).set(user.model_dump())
        # RespondUser(success=True, data=[], message="")
        return Respond(
            success=True,
            data=signJWT(
                user.id, user.username, user.isAuthorized, user.origin, user.type
            ),
            message="The user has been created successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@user.post("/login")
def user_login(user: UserLoginSchema = Body(default=None)):
    if check_user(user):
        data = get_user_byUsername(user.username)

        return Respond(
            success=True,
            data=signJWT(
                data.id, data.username, data.isAuthorized, data.origin, data.type
            ),
            message="The User has been Loged Succesfully",
        )
    else:
        raise HTTPException(status_code=404, detail="User not Found")


def get_user_byUsername(username: str):
    docs = db.collection("users").where("username", "==", username).get()
    users = []
    for doc in docs:
        user = doc.to_dict()
        user["id"] = doc.id
        # Convert the user to a DtoUser object.
        dto_user = DtoUser(**user)
        users.append(dto_user)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return dto_user


def search_username(username):
    collection = db.collection("users")
    doc_ref = collection.where("username", "==", username).get()
    doc = doc_ref[0] if doc_ref else None
    return doc if doc is not None else None


def search_password(password):
    collection = db.collection("users")
    doc_ref = collection.where("user_password", "==", password).get()
    doc = doc_ref[0] if doc_ref else None

    return doc if doc is not None else None


def check_user(data: UserLoginSchema):
    username = search_username(data.username)
    password = search_password(data.password)

    if username is None or password is None:
        return False

    username_value = username.get("username")
    password_value = password.get("user_password")

    if data.username == username_value and data.password == password_value:
        return True
    else:
        return False


# ----------------------------------------------------------------


# Metodos Get User
@user.get("/get_users", dependencies=[Depends(JWTBearer())])
def get_user(db: firestore.Client = Depends(get_db)):
    docs = db.collection("users").get()

    users = []
    for doc in docs:
        user = doc.to_dict()
        user["id"] = doc.id

        # Convert the user to a DtoUser object.
        dto_user = DtoUser(**user)

        users.append(dto_user)

    if not users:
        raise HTTPException(status_code=404, detail="Users not found")

    return ApiResponseDto(success=True, data=users, message="")


@user.get("/get_byId/{user_id}", dependencies=[Depends(JWTBearer())])
async def get_by_Id(user_id: str, db: firestore.Client = Depends(get_db)):
    users_ref = db.collection("users").document(user_id)

    # Get the document with the specified ID.
    doc = users_ref.get()

    # If the document does not exist, raise a 404 error.
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the document as JSON.
    user = doc.to_dict()
    user["id"] = doc.id

    # Convert the user to a DtoUser object.
    dto_user = DtoUser(**user)
    value = dto_user.model_dump()
    return Respond(success=True, data=value, message="")


# ----------------------------------------------------------------

# Metodos Post User


# ----------------------------------------------------------------


# Metodos Put User


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
    return Respond(
        success=True, data=None, message="The User Has Been Updated Succesfully"
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

    # Return the respond
    return Respond(
        success=True, data=None, message="The User Has Been deleted Successfully"
    )


# ----------------------------------------------------------------


@user.get("/test")
def test():
    return Respond(success=True, data=None, message="Nice test")
