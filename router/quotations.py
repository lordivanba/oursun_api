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
from models.quotation import Quotation


quotations = APIRouter()
db = firestore.client()



@quotations.get("/test")
def test():
    return Respond(success=True, data=None, message="Nice test")


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
    
    # Fetch username from "users" table
    username_doc = db.collection("users").document(data.user_id).get()
    username_user = username_doc.get("username")
    
    # Fetch name from "kits" table
    kit_doc = db.collection("kits").document(data.kit_id).get()
    kit_name = kit_doc.get("name")
    

    quotation = Quotation(
        id=str(uuid.uuid4()),
        created_at=str(datetime.datetime.now().strftime("%Y-%m-%d")),
        kit_id=data.kit_id,
        name_kit= kit_name,
        user_id=data.user_id,
        username= username_user
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
        quotation["id"] = doc.id
        dto_quotation = Quotation(**quotation)
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

    dto_quotation = Quotation(**quotation)
    value = dto_quotation.model_dump()
    return Respond(success=True, data=value, message="message")
