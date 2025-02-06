from fastapi import APIRouter
from app.types.zone_types import ZoneType, create_zone_bbox, zone_factory
from app.client.weather import get_weather_by_bbox
from app.client.mongo import mongo_db

router = APIRouter()


@router.get("/near_zones")
async def near_zones(lat: float, lon: float, radius: float):
    """
    Find zones within a specified radius from a given latitude and longitude.
    This function retrieves all zones from the database and checks if their center points
    fall within the specified radius from the given latitude and longitude. The center point
    of a zone is calculated as the midpoint between its south-west and north-east bounding box coordinates.
    Args:
        lat (float): Latitude of the center point to search from.
        lon (float): Longitude of the center point to search from.
        radius (float): Radius within which to search for zones.
    Returns:
        list: A list of zones that fall within the specified radius.
    Note:
        This function uses a naive approach to calculate the distance, which is checked against
        the middle point of each zone's bounding box.
    """

    zones = await mongo_db.get_all_zones()
    zones_in_radius = []
    for zone in zones:
        zone_center_lat = (zone.bbox.south_west.lat + zone.bbox.north_east.lat) / 2
        zone_center_lon = (zone.bbox.south_west.lon + zone.bbox.north_east.lon) / 2
        distance = ((zone_center_lat - lat) ** 2 + (zone_center_lon - lon) ** 2) ** 0.5
        if distance <= radius:
            zones_in_radius.append(zone)

    return zones_in_radius


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
    """

    try:
        zone = zone_factory(zone_id="", zone_name=zone_name, zone_type=zone_type, zone_bbox=create_zone_bbox(zone_rect))
        if zone.zone_type != ZoneType.EMPTY:
            weather = get_weather_by_bbox(zone.bbox)
            zone.set_payload(weather)
        zone = await mongo_db.insert_zone(zone)

    except Exception as e:
        return {"status": "error", "message": str(e)}

    return zone


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

        weather = None
        if zone_type != ZoneType.EMPTY:
            weather = get_weather_by_bbox(zone.bbox)

        new_zone = zone_factory(
            zone_id=zone_id,
            zone_name=zone_name,
            zone_type=zone_type,
            zone_bbox=zone.bbox,
            payload=weather,
        )

        if await mongo_db.update_zone(new_zone) is False:
            return {"status": "error", "message": "Zone not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return new_zone
