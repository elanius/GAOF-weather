from dataclasses import asdict
import os
from typing import Dict

from app.db.zone_types import ZoneBase
from motor.motor_asyncio import AsyncIOMotorClient


class ZoneException(Exception):
    pass


class Zones:
    def __init__(self, connection_string: str):
        self._client = AsyncIOMotorClient(connection_string, uuidRepresentation="standard")
        self._db = self._client["gaof-db"]
        self._zones_collection = self._db["zones"]
        self._zone_store: Dict[str, ZoneBase] = {}
        self._next_id = 0

    def __iter__(self):
        return iter(self._zone_store.values())

    def __getitem__(self, name):
        return self._zone_store[name]

    def unique_id(self) -> int:
        self._next_id += 1
        return self._next_id

    async def add_zone(self, zone: ZoneBase):
        await self._zones_collection.insert_one(asdict(zone))
        # if zone.name in self._zone_store:
        #     raise ZoneException(f"Zone with name {zone.name} already exists")

        # self._zone_store[zone.name] = zone

    def delete_zone(self, name):
        if name not in self._zone_store:
            raise ZoneException(f"Zone with name {name} not found")

        del self._zone_store[name]

    def get_near_zones(self, lat, lon, radius):
        pass


zones_db = Zones(os.getenv("MONGODB_CONNECTION_STRING"))
