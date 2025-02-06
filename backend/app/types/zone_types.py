import dacite
from enum import StrEnum
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class GeoPoint:
    lat: float
    lon: float


class ZoneType(StrEnum):
    EMPTY = "empty"
    WIND = "wind"
    RAIN = "rain"
    VISIBILITY = "visibility"
    TEMPERATURE = "temperature"
    # SPEED_LIMIT = "speed_limit"
    # ALTITUDE_LIMIT = "altitude_limit"
    # NO_FLY = "no_fly"


@dataclass
class ZoneBBox:
    south_west: GeoPoint
    north_east: GeoPoint


@dataclass
class Zone:
    id: str
    name: str
    zone_type: ZoneType
    bbox: ZoneBBox
    payload: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["zone_type"] = self.zone_type.value
        if self.payload:
            data["payload"] = asdict(self.payload)
        return data

    def from_dict(cls, data: dict) -> "Zone":
        return dacite.from_dict(cls, data)

    def set_payload(self, payload: dict):
        if self.zone_type == ZoneType.EMPTY:
            self.payload = None
        elif self.zone_type == ZoneType.WIND:
            self.payload = WindPayload(
                wind_speed=payload["wind"]["speed"],
                wind_direction=payload["wind"]["deg"],
            )
        elif self.zone_type == ZoneType.RAIN:
            self.payload = RainPayload(
                precipitation=payload["rain"]["1h"] if "rain" in payload else 0,
            )
        elif self.zone_type == ZoneType.VISIBILITY:
            self.payload = VisibilityPayload(
                distance=payload["visibility"],
            )
        elif self.zone_type == ZoneType.TEMPERATURE:
            self.payload = TemperaturePayload(
                temp=payload["main"]["temp"],
                temp_min=payload["main"]["temp_min"],
                temp_max=payload["main"]["temp_max"],
                pressure=payload["main"]["pressure"],
                humidity=payload["main"]["humidity"],
            )


@dataclass
class WindPayload:
    wind_speed: float  # meter/second
    wind_direction: float


@dataclass
class RainPayload:
    precipitation: float  # mm/hour


@dataclass
class VisibilityPayload:
    distance: int  # meters


@dataclass
class TemperaturePayload:
    temp: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


type_mapping = {
    ZoneType.WIND: WindPayload,
    ZoneType.RAIN: RainPayload,
    ZoneType.VISIBILITY: VisibilityPayload,
    ZoneType.TEMPERATURE: TemperaturePayload,
}


def create_zone_bbox(zone_rect: list[float]) -> ZoneBBox:
    return ZoneBBox(
        south_west=GeoPoint(lat=zone_rect[0], lon=zone_rect[1]),
        north_east=GeoPoint(lat=zone_rect[2], lon=zone_rect[3]),
    )


def zone_factory(zone_id: str, zone_name: str, zone_type: ZoneType, zone_bbox: ZoneBBox, payload: dict = None) -> Zone:
    zone = Zone(
        id=zone_id,
        name=zone_name,
        zone_type=zone_type,
        bbox=zone_bbox,
    )

    if payload:
        zone.set_payload(payload)

    return zone
