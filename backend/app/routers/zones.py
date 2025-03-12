import math
import logging
from fastapi import APIRouter, HTTPException
from app.types.zone_types import (
    AutoGroupPayload,
    AutoGroupRequest,
    CreateZoneRequest,
    Zone,
    ZoneType,
    create_zone_bbox,
)
from app.client.weather import get_weather_by_bbox
from app.client.mongo import mongo_db
from geopy.distance import geodesic
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/near_zones")
async def near_zones(lat: float, lon: float, radius: float, include_inactive: bool = False):
    """
    Find zones within a specified radius of a given latitude and longitude.

    Args:
        lat (float): The latitude of the point to search around.
        lon (float): The longitude of the point to search around.
        radius (float): The radius within which to search for zones.
        include_inactive (bool): Whether to include inactive zones in the search.
    Returns:
        list: A list of zones that are within the specified radius of the given point.
    """

    zones = await mongo_db.get_all_zones()
    expanded_zones: list[Zone] = []
    for zone in zones:
        if zone.zone_type == ZoneType.AUTO_GROUP:
            expanded_zones.extend(zone.payload.zones)
        else:
            expanded_zones.append(zone)

    zones_in_radius = []
    for zone in expanded_zones:
        if zone.active or include_inactive:
            if is_zone_in_radius(zone, lat, lon, radius):
                zones_in_radius.append(zone)

    return zones_in_radius


def is_zone_in_radius(zone: Zone, lat: float, lon: float, radius: float):
    zone_center_lat = (zone.bbox.south_west.lat + zone.bbox.north_east.lat) / 2
    zone_center_lon = (zone.bbox.south_west.lon + zone.bbox.north_east.lon) / 2
    zone_radius = (
        geodesic(
            (zone.bbox.south_west.lat, zone.bbox.south_west.lon), (zone.bbox.north_east.lat, zone.bbox.north_east.lon)
        ).meters
        / 2
    )
    distance = geodesic((lat, lon), (zone_center_lat, zone_center_lon)).meters

    return distance <= radius + zone_radius


@router.get("/list_zones")
async def list_zones():
    """
    Retrieve a list of all zones.

    Returns:
        list: A list of all zones from the database.
    """

    out_zones = list()
    zones = await mongo_db.get_all_zones()
    for zone in zones:
        out_zones.append(zone)

        if zone.zone_type == ZoneType.AUTO_GROUP:
            payload: AutoGroupPayload = zone.payload
            # TODO evaluate if zone is active according to threshold limits
            out_zones.extend(payload.zones)

    return out_zones


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
        logger.error("Error creating zone", exc_info=e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

    return {"status": "success"}


@router.post("/create_zone")
async def create_zone(request: CreateZoneRequest):
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
        weather = None
        zone_bbox = create_zone_bbox(request.zone_rect)
        if request.zone_type != ZoneType.EMPTY:
            weather = await get_weather_by_bbox(zone_bbox)

        zone = Zone(
            name=request.zone_name,
            zone_type=request.zone_type,
            bbox=zone_bbox,
        )

        zone.set_weather_payload(weather)

        return await mongo_db.insert_zone(zone)

    except Exception as e:
        logger.error("Error creating zone", exc_info=e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


@router.post("/create_auto_group_zone")
async def create_auto_group_zone(request: AutoGroupRequest):
    try:
        zone = Zone(
            name=request.name,
            zone_type=ZoneType.AUTO_GROUP,
            bbox=create_zone_bbox(request.rect),
        )

        payload = AutoGroupPayload(
            sampling_size=request.sampling_size,
            refresh_rate=request.refresh_rate,
            threshold=request.threshold,
            sub_zone_type=request.sub_zone_type,
            zones=create_sub_zones(request.name, request.sub_zone_type, request.rect, request.sampling_size),
        )

        zone.payload = payload
        return await mongo_db.insert_zone(zone)

        # TODO notify weather refresh background task about new auto group zone

    except Exception as e:
        logger.error("Error creating zone", exc_info=e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})


def create_sub_zones(zone_name: str, zone_type: ZoneType, rect: list[float], sampling_size: int) -> list[Zone]:
    # Calculate the width and height of the zone in meters
    width = geodesic((rect[0], rect[1]), (rect[0], rect[3])).meters
    height = geodesic((rect[0], rect[1]), (rect[2], rect[1])).meters

    # Calculate the number of rectangles along width and height
    num_rects_width = int(width / sampling_size) if width >= sampling_size else 1
    num_rects_height = int(height / sampling_size) if height >= sampling_size else 1

    # Create the set of rectangles
    rect_width = width / num_rects_width
    rect_height = height / num_rects_height

    zones = list()
    for i in range(num_rects_width):
        for j in range(num_rects_height):
            sw_lat = rect[0] + (j * rect_height / 111320)  # Convert meters to degrees
            sw_lon = rect[1] + (i * rect_width / (111320 * math.cos(math.radians(rect[0]))))
            ne_lat = sw_lat + (rect_height / 111320)
            ne_lon = sw_lon + (rect_width / (111320 * math.cos(math.radians(sw_lat))))
            zones.append(
                Zone(
                    _id=ObjectId(),
                    name=f"{zone_name}_{i}_{j}",
                    zone_type=zone_type,
                    bbox=create_zone_bbox([sw_lat, sw_lon, ne_lat, ne_lon]),
                    active=False,  # sub-zones are inactive by default
                )
            )

    return zones


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

        update = False
        if zone.name != zone_name:
            zone_name == zone_name
            update = True

        if zone.zone_type != zone_type:
            zone.zone_type = zone_type
            update = True

        if update:
            if await mongo_db.update_zone(zone) is False:
                return {"status": "error", "message": "Zone not found"}
        else:
            return {"status": "success", "message": "No changes to update"}
    except Exception as e:
        logger.error("Error creating zone", exc_info=e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

    return zone


@router.put("/refresh_zone")
async def refresh_zone(zone_id: str):
    """
    Refresh weather data for a zone by its ID.

    Args:
        zone_id (str): The ID of the zone to refresh.

    Returns:
        dict: A dictionary with the status of the operation and updated zone data.
                If successful, returns {"status": "success", "zone": zone}.
                If an error occurs, returns {"status": "error", "message": str(e)}.
    """
    try:
        if (zone := await mongo_db.get_zone(zone_id)) is None:
            return {"status": "error", "message": "Zone not found"}

        weather = await get_weather_by_bbox(zone.bbox)
        zone.set_weather_payload(weather)

        if await mongo_db.update_zone(zone) is False:
            return {"status": "error", "message": "Failed to update zone"}

    except Exception as e:
        logger.error("Error creating zone", exc_info=e)
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

    return zone
