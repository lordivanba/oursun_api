import uuid
import fastapi
import firebase_admin

from firebase_admin import firestore
from fastapi import APIRouter, Depends, File, HTTPException
from auth.jwt_bearer import JWTBearer
from dto.api_response_dto import ApiResponseDto

from dto.respond import Respond
from dto.reviewCreateRequestDto import ReviewCreateRequestDto
from models.review import Review

db = firestore.client()
reviews = APIRouter()


@reviews.get("/test")
def test():
    return Respond(success=True, data=None, message="Nice test")


@reviews.post("/create",  dependencies=[Depends(JWTBearer())])
def create_review(data: ReviewCreateRequestDto):
    review = Review(
        id=str(uuid.uuid4()),
        panels_number=data.panels_number,
        location=data.location,
        payment_type=data.payment_type,
        previous_bill=data.previous_bill,
        current_bill=data.current_bill,
        total_savings=data.total_savings,
    )
    response_data = review.model_dump()
    doc_ref = db.collection("reviews").document(review.id).set(response_data)
    return Respond(success=True, data=None, message="Review Created Succesfully")


@reviews.get("", dependencies=[Depends(JWTBearer())])
def get_reviews():
    docs = db.collection("reviews").get()
    reviews = []
    for doc in docs:
        review = doc.to_dict()
        review["id"] = doc.id
        dto_quotation = Review(**review)
        reviews.append(dto_quotation)
    if not reviews:
        return Respond(success=False, data=None, message="Reviews not found")
    return ApiResponseDto(success=True, data=reviews, message="message")


@reviews.get("/{review_id}", dependencies=[Depends(JWTBearer())])
def get_by_id(review_id: str):
    doc_ref = db.collection("reviews").document(review_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")
    review = doc.to_dict()
    review_dto = Review(**review)
    value = review_dto.model_dump()

    return Respond(success=True, data=value, message="message")


@reviews.put("/{review_id}", dependencies=[Depends(JWTBearer())])
def update_review(review_id: str, data: ReviewCreateRequestDto):
    doc_ref = db.collection("reviews").document(review_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")
    data = {
        "panels_number" : data.panels_number,
        "location": data.location,
        "payment_type": data.payment_type,
        "previous_bill" : data.previous_bill,
        "current_bill": data.current_bill,
        "total_savings": data.total_savings
    }
    doc_ref.update(data)
    
    return Respond(success=True, data=None, message="The review has been update succesfully")
    


@reviews.delete("/{review_id}", dependencies=[Depends(JWTBearer())])
def kit_delete(review_id: str):
    doc_ref = db.collection("reviews").document(review_id)

    # Check if the document exists.
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")

    doc_ref.delete()

    # Return the respond
    return Respond(
        success=True, data=None, message="The Review Has Been deleted Successfully"
    )
