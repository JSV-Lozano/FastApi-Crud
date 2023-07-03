from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.user import User as UserModel
from jwt_manager import create_token
from fastapi.responses import JSONResponse
from pydantic import BaseModel

users_router = APIRouter()


class User(BaseModel):
    email: str
    password: str

# los tags nos permite agrupar las rutas de la aplicacion
@users_router.get("/", tags=["Home"])
def hello_world():
    return JSONResponse(content={"message": "Hello World"}, status_code=200)


@users_router.post("/login", tags=["Auth"])
def login(user: User):
    try:
        if user.email != "admin@gmail.com" or user.password != "admin":
            return JSONResponse(content={"Error": "Usuario o contraseña incorrectos"}, status_code=401)
        token: str = create_token(user.dict())
        return JSONResponse(content=token, status_code=200)
    except StopIteration:
        return JSONResponse(content={"Error": "Usuario o contraseña incorrectos"}, status_code=401)
