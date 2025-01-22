from fastapi import APIRouter
from app.db.zone_types import WindZone, ZoneBBox, ZoneType, GeoPoint
from app.db.zones import ZoneException, zones_db

router = APIRouter()


@router.get("/near_zones")
def near_zones(lat: float, lon: float, radius: float):

    found_zones = zones_db.get_near_zones(lat, lon, radius)

    return found_zones


@router.get("/list_zones")
def list_zones():
    return [zone for zone in zones_db]


@router.post("/create_wind_zone")
async def create_wind_zone(zone_rect: list[float], zone_name: str, wind_speed: float, wind_direction: float):
    """
    Create a wind zone with specified parameters.

    Args:
        zone_rect (list[float]): A list of four floats representing the bounding box of the zone.
            The list should contain [south_west_lat, south_west_lon, north_east_lat, north_east_lon].
        wind_speed (float): The speed of the wind in the zone.
        wind_direction (float): The direction of the wind in the zone.

    Returns:
        dict: A dictionary with the status of the operation. If successful, returns {"status": "success"}.
              If an error occurs, returns {"status": "error", "message": str(e)}.

    Raises:
        ZoneException: If there is an error adding the zone to the database.
    """
    zone = WindZone(
        name=zone_name,
        zone_type=ZoneType.WIND,
        bbox=ZoneBBox(
            south_west=GeoPoint(lat=zone_rect[0], lon=zone_rect[1]),
            north_east=GeoPoint(lat=zone_rect[2], lon=zone_rect[3]),
        ),
        wind_speed=wind_speed,
        wind_direction=wind_direction,
    )

    try:
        await zones_db.add_zone(zone)
    except ZoneException as e:
        return {"status": "error", "message": str(e)}

    return {"status": "success"}
