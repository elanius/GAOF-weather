from fastapi import FastAPI
from app.routers import root, weather

app = FastAPI()

app.include_router(root.router)
app.include_router(weather.router)
