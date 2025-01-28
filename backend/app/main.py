from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

origins = [
    "http://localhost:8000",  # React frontend running on this port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
