from typing import Union

from fastapi import FastAPI
from router import user

from router import kits

app = FastAPI()

@app.router.get("/", tags="/")
def read():
    return {"hello": "world"}

app.include_router(kits.router,prefix="/kits", tags=["kits"])
app.include_router(user.user, prefix="/users", tags=["users"])
