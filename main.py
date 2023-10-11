from typing import Union

from fastapi import FastAPI
<<<<<<< HEAD
=======
from router.user_route import user
>>>>>>> 8461ead (Cambios estructura router User)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bambam")
def bambam():
    return {
        "success": True,
        "data": [
            {
                "user": "bambam",
                "email": "hello@bambamcodes.com",
                "createdAt": "29/09/2023",
            }
        ],
        "pagination": {
            "page": 1,
            "total": 1,
        },
    }


@app.get("/items/{item_id}")
def read_item(
    item_id: int,
    q: Union[str, None] = None,
):
    return {
        "item_id": item_id,
        "q": q,
    }
