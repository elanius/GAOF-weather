from enum import StrEnum
from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class GeoPoint:
    lat: float
    lon: float


class ZoneType(StrEnum):
    EMPTY = "empty"
    WIND = "wind"
    RAIN = "rain"
    VISIBILITY = "visibility"
    # SPEED_LIMIT = "speed_limit"
    # ALTITUDE_LIMIT = "altitude_limit"
    # NO_FLY = "no_fly"


@dataclass
class ZoneBBox:
    south_west: GeoPoint
    north_east: GeoPoint


@dataclass
class ZoneBase:
    id: str
    name: str
    zone_type: ZoneType
    bbox: ZoneBBox

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["zone_type"] = self.zone_type.value
        return data


@dataclass
class WindZone(ZoneBase):
    wind_speed: float  # meter/second
    wind_direction: float

    def __post_init__(self):
        self.zone_type = ZoneType.WIND


@dataclass
class RainZone(ZoneBase):
    precipitation: float  # mm/hour

    def __post_init__(self):
        self.zone_type = ZoneType.RAIN


@dataclass
class VisibilityZone(ZoneBase):
    distance: int  # meters

    def __post_init__(self):
        self.zone_type = ZoneType.VISIBILITY
