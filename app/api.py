from typing import Union
from fastapi import FastAPI
from router import user

from router import kits

app = FastAPI()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to oursun api"}


app.include_router(kits.router, prefix="/kits", tags=["kits"])
app.include_router(user.user, prefix="/users", tags=["users"])
