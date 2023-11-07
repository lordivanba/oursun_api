import fastapi
import firebase_admin

from firebase_admin import firestore
from fastapi import APIRouter, Depends, File, HTTPException

from dto.respond import Respond


quotations = APIRouter()
db = firestore.client()

@quotations.get("/test")
def test():
    return Respond(success=True, data=None, message="Nice test")
