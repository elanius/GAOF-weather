from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import root, weather, zones


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # teardown
    pass


app = FastAPI(lifespan=lifespan)

app.include_router(root.router)
app.include_router(weather.router)
app.include_router(zones.router)
