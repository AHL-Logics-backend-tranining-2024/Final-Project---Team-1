from fastapi import FastAPI
from .database import engine
from . import models
from .api.routes import *
from app.api.main import api_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



app.include_router(api_router, prefix="/api/v1")