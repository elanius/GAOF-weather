from setuptools import setup, find_packages

setup(
    name="Drone-weather-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "runserver=app.main:app",
        ],
    },
)
