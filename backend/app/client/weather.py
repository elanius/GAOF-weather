import os
import requests
from fastapi import HTTPException

from app.db.zone_types import GeoPoint, RainZone, VisibilityZone, WindZone, ZoneBBox, ZoneBase, ZoneType


OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")


def get_weather_by_bbox(bbox: ZoneBBox):
    mid_lat = (bbox.south_west.lat + bbox.north_east.lat) / 2
    mid_lon = (bbox.south_west.lon + bbox.north_east.lon) / 2

    return get_weather_by_coordinates(mid_lat, mid_lon)


def get_weather_by_coordinates(lat: float, lon: float):
    if not OPEN_WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API key not found")

    url = (
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPEN_WEATHER_API_KEY}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()


def create_weather_zone(zone_id: str, zone_rect: list[float], zone_name: str, zone_type: ZoneType) -> ZoneBase:
    if len(zone_rect) != 4:
        raise HTTPException(status_code=400, detail="Invalid zone rectangle")

    zone_bbox = ZoneBBox(
        south_west=GeoPoint(lat=zone_rect[0], lon=zone_rect[1]),
        north_east=GeoPoint(lat=zone_rect[2], lon=zone_rect[3]),
    )

    weather_data = get_weather_by_bbox(zone_bbox)

    if zone_type == ZoneType.EMPTY:
        return ZoneBase(
            id=zone_id,
            name=zone_name,
            zone_type=zone_type,
            bbox=zone_bbox,
        )
    elif zone_type == ZoneType.WIND:
        return WindZone(
            id=zone_id,
            name=zone_name,
            zone_type=zone_type,
            bbox=zone_bbox,
            wind_speed=weather_data["wind"]["speed"],
            wind_direction=weather_data["wind"]["deg"],
        )
    elif zone_type == ZoneType.RAIN:
        return RainZone(
            id=zone_id,
            name=zone_name,
            zone_type=zone_type,
            bbox=zone_bbox,
            precipitation_1h=weather_data["rain"]["1h"] if "rain" in weather_data else 0,
        )
    elif zone_type == ZoneType.VISIBILITY:
        return VisibilityZone(
            id=zone_id,
            name=zone_name,
            zone_type=zone_type,
            bbox=zone_bbox,
            distance=weather_data["visibility"],
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid zone type")
