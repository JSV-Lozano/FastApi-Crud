from fastapi import APIRouter
from models.movies import Movies as MoviModel
from middleware.jwt_bearer import JWTBearer
from fastapi import Path, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from config.database import Session
from sqlalchemy.orm.exc import NoResultFound

# Creamos la Ruta
movie_router = APIRouter()


class Movies(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=1, max_length=50)
    overview: str
    year: int
    rating: float
    category: str


@movie_router.get("/movies", tags=["Movies"], response_model=List[Movies], status_code=200, dependencies=[Depends(JWTBearer())])
def movie() -> List[Movies]:
    db = Session()
    result = db.query(MoviModel).all()
    print(jsonable_encoder(result))
    return JSONResponse(content=jsonable_encoder(result), status_code=200)


@movie_router.get("/movies/{id}}", tags=["Movies"], response_model=Movies)
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


@movie_router.get("/movies/", tags=["Movies"], response_model=List[Movies])
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


@movie_router.post("/movies", tags=["Movies"], response_model=dict, status_code=201)
def movie_create(movie: Movies) -> dict:
    try:
        db = Session()
        # Usamos ** para extraer los atributos para no pasarlos uno por uno manualmente
        new_movie = MoviModel(**movie.dict())
        db.add(new_movie)
        db.commit()
        return JSONResponse(content={"Message": "Pelicula creada"}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"Message": e}, status_code=400)


@movie_router.delete("/movies/{id}}", tags=["Movies"], response_model=dict)
def movie_delete(id: int) -> dict:
    try:
        db = Session()
        result = db.query(MoviModel).filter(MoviModel.id == id).first()
        if not result:
            raise NoResultFound
        db.delete(result)
        db.commit()
        return JSONResponse(content={"Message": "Pelicula eliminada"}, status_code=200)
    except NoResultFound:
        return JSONResponse(content={"Message": "Pelicula no encontrada"}, status_code=404)


@movie_router.put("/movies/{id}}", tags=["Movies"], response_model=dict, status_code=200)
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
