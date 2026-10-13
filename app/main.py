from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="keepy", lifespan=lifespan)
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello, keepy!"}
