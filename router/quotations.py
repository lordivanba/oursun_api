import datetime
import uuid
import fastapi
import firebase_admin

from firebase_admin import firestore
from fastapi import APIRouter, Depends, File, HTTPException
from auth.jwt_bearer import JWTBearer
from dto.api_response_dto import ApiResponseDto
from dto.quotationsCreateRequestDto import QuotationsCreateRequestDto

from dto.respond import Respond
from dto.responseQuotationsDto import ResponseQuotationsDto
from models.kit import Kit
from models.quotation import Quotation
from models.user import User


quotations = APIRouter()
db = firestore.client()


@quotations.get("/test")
def test():
    return Respond(success=True, data=None, message="Nice test")


def search_kit(id: str):
    doc_ref = db.collection("kits").document(id)
    doc = doc_ref.get()
    if not doc.exists:
        return "", 0
    kit = doc.to_dict()
    # Convert the kit to a kit object.
    dto_kit = Kit(**kit)
    return dto_kit.name, dto_kit.price


def search_username(id: str):
    doc_ref = db.collection("users").document(id)
    doc = doc_ref.get()
    if not doc.exists:
        return ""
    user = doc.to_dict()
    # Convert the user to a kit object.
    dto_user = User(**user)
    return dto_user.username


@quotations.post("/upload", dependencies=[Depends(JWTBearer())])
def create_quotation(data: QuotationsCreateRequestDto):
    # Validate if kit_id Exists
    kit_ref = db.collection("kits").where("id", "==", data.kit_id).get()
    if not kit_ref:
        raise HTTPException(status_code=404, detail="Kit not found")
    # Validate if user_id Exists
    user_ref = db.collection("users").where("id", "==", data.user_id).get()
    if not user_ref:
        raise HTTPException(status_code=404, detail="User not found")

    quotation = Quotation(
        id=str(uuid.uuid4()),
        created_at=str(datetime.datetime.now().strftime("%Y-%m-%d")),
        kit_id=data.kit_id,
        user_id=data.user_id,
    )

    response_data = quotation.model_dump()
    doc_ref = db.collection("quotations").document(quotation.id).set(response_data)
    return Respond(success=True, data=None, message="Quotation Created Succesfully ")


@quotations.get("/get_all", dependencies=[Depends(JWTBearer())])
def get_quotations():
    docs = db.collection("quotations").get()
    quotations = []
    for doc in docs:
        quotation = doc.to_dict()
        value_quotation = Quotation(**quotation)
        kit_name, kit_price = search_kit(value_quotation.kit_id)
        username = search_username(value_quotation.user_id)

        dto_quotation = ResponseQuotationsDto(
            id=value_quotation.id,
            created_at=value_quotation.created_at,
            kit_id=value_quotation.kit_id,
            kit_name=kit_name,
            kit_price=kit_price,
            user_id=value_quotation.user_id,
            username=username,
        )
        if dto_quotation.kit_name == "" and dto_quotation.kit_price == 0 or dto_quotation.username == "":
            pass
        else:
            quotations.append(dto_quotation)
        
        

    if not quotations:
        return Respond(success=False, data=None, message="Quotations not found")

    return ApiResponseDto(success=True, data=quotations, message="message")


@quotations.get("/get_by_id/{quotation_id}", dependencies=[Depends(JWTBearer())])
def get_by_id(quotation_id: str):
    doc_ref = db.collection("quotations").document(quotation_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Quotation not found")
    quotation = doc.to_dict()

    value_quotation = Quotation(**quotation)
    kit_name, kit_price = search_kit(value_quotation.kit_id)
    username = search_username(value_quotation.user_id)

    dto_quotation = ResponseQuotationsDto(
        id=value_quotation.id,
        created_at=value_quotation.created_at,
        kit_id=value_quotation.kit_id,
        kit_name=kit_name,
        kit_price=kit_price,
        user_id=value_quotation.user_id,
        username=username,
    )
    value = dto_quotation.model_dump()
    return Respond(success=True, data=value, message="message")
