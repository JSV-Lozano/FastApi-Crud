from fastapi import FastAPI
from middleware.error_handler import ErrorHandler
from config.database import engine, Base
from routers.movie import movie_router
from routers.users import users_router

# Creacion de la aplicacion
app = FastAPI()
# Para cambiar el nombre de la aplicacion
app.title = "Movies API"
# Para cambiar la version de la aplicacion
app.version = "0.0.1"
# sql
Base.metadata.create_all(bind=engine)
# Middleware
app.add_middleware(ErrorHandler)
# Rutas
app.include_router(movie_router)
app.include_router(users_router)
