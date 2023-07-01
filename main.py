import json
from fastapi import FastAPI, Body, Path, Query, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Optional, List
from pydantic import BaseModel, Field, validator, ValidationError
from jwt_manager import create_token, validate_token
from config.database import Session, engine, Base
from models.movies import Movies as MoviModel
from models.user import User as UserModel
from sqlalchemy.orm.exc import NoResultFound


class Movies(BaseModel):
    id: Optional[int] = None
    title: str = Field(default="The Matris", min_length=1, max_length=50)
    overview: str
    year: int
    rating: float
    category: str

    class Config:
        schema_extra = {
            "example": {
                "id": 0,
                "title": "The Matrix",
                "overview": "A movie about the Matrix",
                "year": 1999,
                "rating": 8.7,
                "category": "Action"
            }
        }

    @validator('title', 'overview', 'year', 'rating', 'category')
    def validate_empty_values(cls, value):
        if not value:
            raise ValueError("El valor no puede estar vacío")
        return value


class User(BaseModel):
    email: str
    password: str


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data["email"] != "admin@gmail.com":
            raise HTTPException(
                status_code=403, detail="Credenciales invalidas")


app = FastAPI()


def movies():
    with open("db.json", 'r') as file:
        data = json.load(file)
    return data["movies"]


# Para cambiar el nombre de la aplicacion
app.title = "Movies API"

# Para cambiar la version de la aplicacion
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

# los tags nos permite agrupar las rutas de la aplicacion


@app.get("/", tags=["Home"])
def hello_world():
    return {"Hello": "World"}


@app.post("/login", tags=["Auth"])
def login(user: User):
    try:
        if user.email == "admin@gmail.com" and user.password == "admin":
            token: str = create_token(user.dict())
            return JSONResponse(content=token, status_code=200)
        else:
            return JSONResponse(content={"Error": "Usuario o contraseña incorrectos"}, status_code=401)
    except StopIteration:
        return {"Error": "Internal error"}
    return user


@app.get("/movies", tags=["Movies"], response_model=List[Movies], status_code=200, dependencies=[Depends(JWTBearer())])
def movie() -> List[Movies]:
    db = Session()
    result = db.query(MoviModel).all()
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@app.get("/movies/{id}}", tags=["Movies"], response_model=Movies)
def movie_id(id: int = Path(ge=0, le=100)) -> Movies:
    try:
        db = Session()
        if result := db.query(MoviModel).filter(MoviModel.id == id).first():
            return JSONResponse(
                content=jsonable_encoder(result), status_code=200)
        else:
            raise NoResultFound
    except NoResultFound:
        return JSONResponse(content={"Message": "Pelicula no encontrada"}, status_code=404)


@app.get("/movies/", tags=["Movies"], response_model=List[Movies])
def movie_category(category: str = Query(min_length=5)) -> List[Movies]:
    try:
        db = Session()
        if (
            result := db.query(MoviModel)
            .filter(MoviModel.category == category)
            .all()
        ):
            return JSONResponse(content=jsonable_encoder(result), status_code=200)
        else:
            raise NoResultFound
    except NoResultFound:
        return JSONResponse(content={"Message": "Categoria no encontrada"}, status_code=404)


@app.post("/movies", tags=["Movies"], response_model=dict, status_code=201)
def movie_create(movie: Movies) -> dict:
    try:
        db = Session()
        # Usamos ** para extraer los atributos para no pasarlos uno por uno manualmente
        new_movie = MoviModel(**movie.dict())
        db.add(new_movie)
        db.commit()
        return {"Mensaje": "Pelicula creada"}
    except Exception as e:
        return JSONResponse(content={"Mensaje": e}, status_code=400)


@app.delete("/movies/{id}}", tags=["Movies"], response_model=dict)
def movie_delete(id: int) -> dict:
    try:
        db= Session()
        result = db.query(MoviModel ).filter(MoviModel.id == id).first()
        if not result:
            raise NoResultFound
        db.delete(result)
        db.commit()
        return JSONResponse(content={"Message": "Pelicula eliminada"}, status_code=200)
    except NoResultFound:
        return JSONResponse(content={"Message": "Pelicula no encontrada"}, status_code=404)


@app.put("/movies/{id}}", tags=["Movies"], response_model=dict, status_code=200)
def movie_update(id: int, movie: Movies) -> dict:
    try:
        db = Session()
        result = db.query(MoviModel).filter(MoviModel.id == id).first()
        if not result:
            raise NoResultFound
        result.title = movie.title
        result.overview = movie.overview
        result.year = movie.year
        result.rating = movie.rating
        result.category = movie.category
        db.commit()
        return JSONResponse(content={"Message": "Pelicula actualizada"}, status_code=200)
    except NoResultFound:
        return JSONResponse(content={"Message": "Pelicula no encontrada"}, status_code=404)
