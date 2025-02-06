import logging
import os
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.types.zone_types import GeoPoint, Zone, ZoneBBox, ZoneType, type_mapping

logger = logging.getLogger(__name__)

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


class MongoDB(object):
    def __init__(self) -> None:
        self._client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING, uuidRepresentation="standard")
        self._db = self._client["gaof-db"]
        self.zones = self._db["zones"]

    def _zone_from_doc(self, doc: dict) -> Zone:
        zone_type = ZoneType(doc["zone_type"])
        return Zone(
            id=str(doc["_id"]),
            name=doc["name"],
            zone_type=zone_type,
            bbox=ZoneBBox(
                south_west=GeoPoint(**doc["bbox"]["south_west"]),
                north_east=GeoPoint(**doc["bbox"]["north_east"]),
            ),
            # This works but only for payloads which doesn't contain other nested objects
            payload=type_mapping[zone_type](**doc["payload"]) if zone_type != ZoneType.EMPTY else None,
        )

    async def get_zone(self, zone_id: str) -> Optional[Zone]:
        zone_doc = await self.zones.find_one({"_id": ObjectId(zone_id)})
        if zone_id:
            return self._zone_from_doc(zone_doc)

        return None

    async def insert_zone(self, zone: Zone) -> Zone:
        zone_dict = zone.to_dict()
        del zone_dict["id"]
        result = await self.zones.insert_one(zone_dict)
        zone.id = str(result.inserted_id)
        return zone

    async def update_zone(self, zone: Zone) -> bool:
        zone_dict = zone.to_dict()
        zone_id = zone_dict.pop("id")
        result = await self.zones.update_one({"_id": ObjectId(zone_id)}, {"$set": zone_dict})
        return result.modified_count > 0

    async def get_all_zones(self) -> list[Zone]:
        return [self._zone_from_doc(zone_doc) for zone_doc in await self.zones.find().to_list()]

    async def delete_zone(self, zone_id: str) -> bool:
        result = await self.zones.delete_one({"_id": ObjectId(zone_id)})
        return result.deleted_count > 0


mongo_db = MongoDB()
