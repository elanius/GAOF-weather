from fastapi import APIRouter
from app.db.zone_types import ZoneType
from app.db.zones import ZoneException, zones_db
from app.client.weather import create_weather_zone
from app.client.mongo import mongo_db

router = APIRouter()


@router.get("/near_zones")
def near_zones(lat: float, lon: float, radius: float):

    found_zones = zones_db.get_near_zones(lat, lon, radius)

    return found_zones


@router.get("/list_zones")
async def list_zones():
    """
    Retrieve a list of all zones.

    Returns:
        list: A list of all zones from the database.
    """
    zones = await mongo_db.get_all_zones()
    return zones


@router.delete("/delete_zone")
async def delete_zone(zone_id: str):
    """
    Delete a zone by its ID.

    Args:
        zone_id (str): The ID of the zone to delete.

    Returns:
        dict: A dictionary with the status of the operation.
                If successful, returns {"status": "success"}.
                If an error occurs, returns {"status": "error", "message": str(e)}.
    """
    try:
        if await mongo_db.delete_zone(zone_id) is False:
            return {"status": "error", "message": "Zone not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "success"}


@router.post("/create_zone")
async def create_zone(zone_rect: list[float], zone_name: str = "", zone_type: ZoneType = ZoneType.EMPTY):
    """
    Create a zone with specified parameters.

    Args:
        zone_rect (list[float]): A list of four floats representing the bounding box of the zone.
            The list should contain [south_west_lat, south_west_lon, north_east_lat, north_east_lon].
        zone_name (str): The name of the zone.
        zone_type (ZoneType): The type of the zone (wind, rain, fog).

    Returns:
        dict: A dictionary with the status of the operation and weather data.
              If successful, returns {"status": "success", "weather": weather_data}.
              If an error occurs, returns {"status": "error", "message": str(e)}.

    Raises:
        ZoneException: If there is an error adding the zone to the database.
    """

    try:
        zone = create_weather_zone("", zone_rect, zone_name, zone_type)
        zone = await mongo_db.insert_zone(zone)

    except ZoneException as e:
        return {"status": "error", "message": str(e)}

    return zone.to_dict()


@router.put("/edit_zone")
async def edit_zone(zone_id: str, zone_type: ZoneType, zone_name: str = ""):
    """
    Edit a zone by its ID.

    Args:
        zone_id (str): The ID of the zone to edit.
        zone_name (str): The new name of the zone.
        zone_type (ZoneType): The new type of the zone.

    Returns:
        dict: A dictionary with the status of the operation.
              If successful, returns {"status": "success"}.
              If an error occurs, returns {"status": "error", "message": str(e)}.
    """
    try:
        if (zone := await mongo_db.get_zone(zone_id)) is None:
            return {"status": "error", "message": "Zone not found"}

        rect = [zone.bbox.south_west.lat, zone.bbox.south_west.lon, zone.bbox.north_east.lat, zone.bbox.north_east.lon]
        new_zone = create_weather_zone(zone.id, rect, zone_name, zone_type)
        if await mongo_db.update_zone(new_zone) is False:
            return {"status": "error", "message": "Zone not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "success"}
