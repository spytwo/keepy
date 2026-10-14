from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth import verify_credentials
from app.database import async_engine
from app.models import Base
from app.routers import router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


app = FastAPI(
    title="keepy", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
)

app.include_router(router, dependencies=[Depends(verify_credentials)])

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/", dependencies=[Depends(verify_credentials)])
async def root():
    return FileResponse(STATIC_DIR / "index.html")
