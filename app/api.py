from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import user

from router import kits

app = FastAPI()

# Configure CORS settings to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to oursun api"}


app.include_router(kits.router, prefix="/kits", tags=["kits"])
app.include_router(user.user, prefix="/users", tags=["users"])