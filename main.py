import json
from fastapi import FastAPI, Body, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field


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


app = FastAPI()


def movies():
    with open("db.json", 'r') as file:
        data = json.load(file)
    return data["movies"]


# Para cambiar el nombre de la aplicacion
app.title = "Movies API"

# Para cambiar la version de la aplicacion
app.version = "0.0.1"

# los tags nos permite agrupar las rutas de la aplicacion


@app.get("/", tags=["Home"])
def hello_world():
    return {"Hello": "World"}


@app.get("/movies", tags=["Movies"], response_model=List[Movies], status_code=200)
def movie() -> List[Movies]:
    return movies()


@app.get("/movies/{id}}", tags=["Movies"], response_model=Movies)
def movie_id(id: int = Path(ge=0, le=100)) -> Movies:
    try:
        return [movie for movie in movies() if movie["id"] == id]
    except StopIteration:
        return {"Error": "Pelicula no encontrada"}


@app.get("/movies/", tags=["Movies"], response_model=List[Movies])
def movie_category(category: str = Query(min_length=5)) -> List[Movies]:
    try:
        return [movie for movie in movies() if movie["category"] == category]
    except StopIteration:
        return {"Error": "Pelicula no encontrada"}


@app.post("/movies", tags=["Movies"], response_model=dict, status_code=201)
def movie_create(movie: Movies) -> dict:
    try:
        with open("db.json", 'r+') as file:
            data = json.load(file)
            data["movies"].append(movie.dict())
            file.seek(0)
            json.dump(data, file, indent=4)
        return {"Mensaje": "Pelicula creada"}
    except StopIteration:
        return {"Error": "Pelicula no creada"}


@app.delete("/movies/{id}}", tags=["Movies"], response_model=dict)
def movie_delete(id: int) -> dict:
    try:
        with open("db.json", 'r+') as file:
            data = json.load(file)
            for movi in data["movies"]:
                if movi["id"] == id:
                    data["movies"].remove(movi)
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    return {"Mensaje": "Pelicula eliminada"}
                else:
                    return {"Error": "Pelicula no encontrada"}
    except StopIteration:
        return {"Error": "Pelicula no eliminada"}


""" new_list = list(filter(lambda x: x["id"] != id, data["movies"]))
            data["movies"] = new_list
            file.seek(0)
            json.dump(data, file, indent=4)
            return {"Mensaje": "Pelicula eliminada"} """


@app.put("/movies/{id}}", tags=["Movies"], response_model=dict, status_code=200)
def movie_update(id: int, movie: Movies) -> dict:
    try:
        with open("db.json", 'r+') as file:
            data = json.load(file)
            for movi in data["movies"]:
                if movi["id"] == id:
                    movi["title"] = movie.title
                    movi["overview"] = movie.overview
                    movi["year"] = movie.year
                    movi["rating"] = movie.rating
                    movi["category"] = movie.category
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    return {"Mensaje": "Pelicula actualizada"}
    except StopIteration:
        return {"Error": "Pelicula no actualizada"}
