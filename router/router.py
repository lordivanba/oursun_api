from fastapi import APIRouter
from models.user import User

user =  APIRouter()

@user.get("/")
def root():
    return {"message": "Hi, I am OurSun Api with a router"}

#Metodos Get User
@user.get("/api/user_id")
def get_user(user_id:int):
    return {"message": user_id}
    
#Metodos Post User
@user.post("/api/user")
def create_user(user: User):
    return user
    
#Metodos Put User
#Metodos Delete User
