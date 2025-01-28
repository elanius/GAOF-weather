import logging
import os
from dacite import from_dict
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.zone_types import RainZone, VisibilityZone, WindZone, ZoneBase, ZoneType

logger = logging.getLogger(__name__)

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


class MongoDB(object):
    def __init__(self) -> None:
        self._client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING, uuidRepresentation="standard")
        self._db = self._client["gaof-db"]
        self.zones = self._db["zones"]

    async def get_zone(self, zone_id: str) -> Optional[ZoneBase]:
        zone_dict = await self.zones.find_one({"_id": ObjectId(zone_id)})
        return self._create_zone(zone_dict) if zone_dict else None

    async def insert_zone(self, zone: ZoneBase) -> ZoneBase:
        zone_dict = zone.to_dict()
        del zone_dict["id"]
        result = await self.zones.insert_one(zone_dict)
        zone.id = str(result.inserted_id)
        return zone

    async def update_zone(self, zone: ZoneBase) -> bool:
        zone_dict = zone.to_dict()
        zone_id = zone_dict.pop("id")
        result = await self.zones.update_one({"_id": ObjectId(zone_id)}, {"$set": zone_dict})
        return result.modified_count > 0

    async def get_all_zones(self) -> list[ZoneBase]:
        return [self._create_zone(zone) for zone in await self.zones.find().to_list(length=None)]

    async def delete_zone(self, zone_id: str) -> bool:
        result = await self.zones.delete_one({"_id": ObjectId(zone_id)})
        return result.deleted_count > 0

    def _create_zone(self, zone_dict: dict) -> ZoneBase:
        zone_type = zone_dict["zone_type"]
        zone_dict["id"] = str(zone_dict["_id"])
        zone_dict["zone_type"] = ZoneType(zone_dict["zone_type"])
        del zone_dict["_id"]
        if zone_type == ZoneType.EMPTY:
            return from_dict(ZoneBase, zone_dict)
        elif zone_type == ZoneType.WIND:
            return from_dict(WindZone, zone_dict)
        elif zone_type == ZoneType.RAIN:
            return from_dict(RainZone, zone_dict)
        elif zone_type == ZoneType.VISIBILITY:
            return from_dict(VisibilityZone, zone_dict)
        else:
            raise ValueError(f"Unknown zone type: {zone_type}")


mongo_db = MongoDB()
