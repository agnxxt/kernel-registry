"""
Spatiotemporal - Time and Location as First-Class Entities

Time and location are fundamental to all decisions, insights, and analysis:
- Time Types (instants, durations, calendars)
- Location Types (points, regions, coordinates)
- Spatiotemporal Reasoning
- Temporal Analysis
- Spatial Analysis
- Time Series
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import math


# ============================================================
# Time Types
# ============================================================

class TimePrecision:
    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"
    MILLISECOND = "millisecond"


@dataclass
class TimeInstant:
    """Time instant"""
    id: str
    
    # Time
    iso: str = ""  # ISO 8601
    epoch: Optional[float] = None
    
    # Components
    year: int = 2024
    month: int = 1
    day: int = 1
    hour: int = 0
    minute: int = 0
    second: int = 0
    
    # Precision
    precision: str = "second"
    
    # Timezone
    timezone: str = "UTC"
    utc_offset: Optional[int] = None
    
    # Label
    label: str = ""
    source: str = ""
    
    def to_datetime(self) -> datetime:
        """Convert to datetime"""
        try:
            return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        except:
            return datetime.now()
    
    def to_epoch(self) -> float:
        """Convert to epoch"""
        return self.to_datetime().timestamp()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "iso": self.iso or self.to_datetime().isoformat(),
            "epoch": self.to_epoch(),
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "timezone": self.timezone,
        }


@dataclass
class Duration:
    """Duration"""
    id: str
    
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    
    total_seconds: Optional[float] = None
    human_readable: str = ""
    
    precision: str = "second"
    
    def calculate_total(self) -> float:
        """Calculate total seconds"""
        days = self.years * 365 + self.months * 30 + self.weeks * 7 + self.days
        seconds = (days * 24 * 3600 + 
                 self.hours * 3600 + 
                 self.minutes * 60 + 
                 self.seconds)
        self.total_seconds = seconds
        return seconds
    
    def to_timedelta(self) -> timedelta:
        """Convert to timedelta"""
        return timedelta(
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
        )
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "years": self.years,
            "months": self.months,
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "total_seconds": self.calculate_total(),
            "human_readable": self.human_readable or f"{self.days}d {self.hours}h {self.minutes}m",
        }


@dataclass
class TimeInterval:
    """Time interval"""
    id: str
    
    start: TimeInstant
    end: TimeInstant
    
    duration: Optional[Duration] = None
    
    relationship: str = "during"  # before, after, during, overlaps, contains, equals
    
    is_instantaneous: bool = False
    is_ongoing: bool = False
    
    def calculate_duration(self) -> Duration:
        """Calculate duration"""
        dur = Duration(
            id=self.id,
            days=(self.end.day - self.start.day),
            hours=self.end.hour - self.start.hour,
            minutes=self.end.minute - self.start.minute,
            seconds=self.end.second - self.start.second,
        )
        dur.calculate_total()
        self.duration = dur
        return dur
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "duration": self.duration.to_dict() if self.duration else None,
            "relationship": self.relationship,
            "is_instantaneous": self.is_instantaneous,
            "is_ongoing": self.is_ongoing,
        }


# ============================================================
# Location Types
# ============================================================

class GeoPrecision:
    CONTINENT = "continent"
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"
    STREET = "street"
    EXACT = "exact"


class GeoCRS:
    WGS84 = "WGS84"


@dataclass
class GeoPoint:
    """Geographic point"""
    id: str
    
    lat: float = 0  # -90 to 90
    lon: float = 0  # -180 to 180
    altitude: Optional[float] = None
    
    precision: str = "city"
    crs: str = "WGS84"
    
    label: str = ""
    address: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon,
            "altitude": self.altitude,
            "precision": self.precision,
            "label": self.label,
            "address": self.address,
        }


@dataclass
class GeoRegion:
    """Geographic region"""
    id: str
    
    north: float = 0
    south: float = 0
    east: float = 0
    west: float = 0
    
    centroid: Optional[GeoPoint] = None
    
    region_type: str = "country"
    name: str = ""
    code: str = ""
    
    parent_region: str = ""
    child_regions: List[str] = field(default_factory=list)
    
    def centroid_calc(self) -> GeoPoint:
        """Calculate centroid"""
        if not self.centroid:
            self.centroid = GeoPoint(
                id=self.id + "_centroid",
                lat=(self.north + self.south) / 2,
                lon=(self.east + self.west) / 2,
            )
        return self.centroid
    
    def contains(self, point: GeoPoint) -> bool:
        """Check if region contains point"""
        return (self.south <= point.lat <= self.north and 
                self.west <= point.lon <= self.east)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "north": self.north,
            "south": self.south,
            "east": self.east,
            "west": self.west,
            "region_type": self.region_type,
            "name": self.name,
            "code": self.code,
        }


@dataclass
class Place:
    """Place"""
    id: str
    
    location: GeoPoint
    
    place_type: str = "residence"
    name: str = ""
    
    properties: Dict = field(default_factory=dict)
    
    operating_hours: str = ""
    timezone: str = "UTC"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "location": self.location.to_dict(),
            "place_type": self.place_type,
            "name": self.name,
            "operating_hours": self.operating_hours,
            "timezone": self.timezone,
        }


class DistanceUnit:
    METERS = "meters"
    KILOMETERS = "kilometers"
    FEET = "feet"
    MILES = "miles"


@dataclass
class Distance:
    """Distance"""
    id: str
    
    value: float = 0
    unit: str = "meters"
    
    total_meters: Optional[float] = None
    
    def calculate_meters(self) -> float:
        """Convert to meters"""
        if self.unit == "kilometers":
            self.total_meters = self.value * 1000
        elif self.unit == "feet":
            self.total_meters = self.value * 0.3048
        elif self.unit == "miles":
            self.total_meters = self.value * 1609.34
        else:
            self.total_meters = self.value
        return self.total_meters
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "value": self.value,
            "unit": self.unit,
            "total_meters": self.calculate_meters(),
        }


# ============================================================
# Spatiotemporal
# ============================================================

@dataclass
class Spatiotemporal:
    """Spatiotemporal entity"""
    id: str
    
    time: Optional[TimeInstant] = None
    time_interval: Optional[TimeInterval] = None
    
    location: Optional[GeoPoint] = None
    region: Optional[GeoRegion] = None
    
    is_spatiotemporal: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "time": self.time.to_dict() if self.time else None,
            "location": self.location.to_dict() if self.location else None,
        }


@dataclass
class Event:
    """Event (spatiotemporal)"""
    id: str
    name: str
    description: str = ""
    
    time_interval: TimeInterval
    
    location: Optional[GeoPoint] = None
    region: str = ""
    
    event_type: str = ""
    properties: Dict = field(default_factory=dict)
    
    participants: List[str] = field(default_factory=list)
    
    impact_radius: Optional[float] = None
    impact_regions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "time_interval": self.time_interval.to_dict(),
            "location": self.location.to_dict() if self.location else None,
            "event_type": self.event_type,
        }


@dataclass
class Trajectory:
    """Trajectory (movement)"""
    id: str
    
    entity_id: str
    waypoints: List[GeoPoint] = field(default_factory=list)
    
    start_time: TimeInstant
    end_time: TimeInstant
    
    duration: Optional[Duration] = None
    distance: Optional[Distance] = None
    
    avg_velocity: Optional[float] = None
    max_velocity: Optional[float] = None
    
    def calculate_distance(self) -> Distance:
        """Calculate total distance"""
        if len(self.waypoints) < 2:
            return Distance(id=self.id, value=0)
        
        total = 0
        for i in range(len(self.waypoints) - 1):
            total += haversine(self.waypoints[i], self.waypoints[i + 1])
        
        self.distance = Distance(id=self.id, value=total, unit="kilometers")
        self.distance.calculate_meters()
        return self.distance
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "waypoint_count": len(self.waypoints),
            "start_time": self.start_time.to_dict(),
            "end_time": self.end_time.to_dict(),
            "distance": self.calculate_distance().to_dict() if self.distance else None,
        }


def haversine(p1: GeoPoint, p2: GeoPoint) -> float:
    """Calculate distance between two points"""
    R = 6371  # Earth radius in km
    
    lat1 = math.radians(p1.lat)
    lat2 = math.radians(p2.lat)
    dlat = math.radians(p2.lat - p1.lat)
    dlon = math.radians(p2.lon - p1.lon)
    
    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


# ============================================================
# Temporal Analysis
# ============================================================

class TimeSeriesFrequency:
    MILLISECOND = "millisecond"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass
class TimeSeriesPoint:
    """Time series point"""
    timestamp: str
    value: float
    
    quality: str = "good"  # good, estimated, interpolated, missing


@dataclass
class TimeSeries:
    """Time series"""
    id: str
    name: str
    
    points: List[TimeSeriesPoint] = field(default_factory=list)
    frequency: str = "day"
    
    def add(self, timestamp: str, value: float, quality: str = "good"):
        """Add point"""
        self.points.append(TimeSeriesPoint(
            timestamp=timestamp,
            value=value,
            quality=quality,
        ))
        self.points.sort(key=lambda p: p.timestamp)
    
    def get_range(self) -> tuple:
        """Get time range"""
        if not self.points:
            return None, None
        return self.points[0].timestamp, self.points[-1].timestamp
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "count": len(self.points),
            "frequency": self.frequency,
            "range": self.get_range(),
        }


# ============================================================
# Spatial Analysis
# ============================================================

class SpatialRelationship:
    EQUALS = "equals"
    WITHIN = "within"
    CONTAINS = "contains"
    OVERLAPS = "overlaps"
    TOUCHES = "touches"
    DISJOINT = "disjoint"
    INTERSECTS = "intersects"
    NEAR = "near"
    ADJACENT = "adjacent"


@dataclass
class Zone:
    """Zone"""
    id: str
    
    region: GeoRegion
    
    zone_type: str = "restricted"
    rules: List[str] = field(default_factory=list)
    
    requires_permission: bool = False
    access_hours: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "region": self.region.to_dict(),
            "zone_type": self.zone_type,
            "requires_permission": self.requires_permission,
        }


# ============================================================
# Factory
# ============================================================

def now() -> TimeInstant:
    """Get current time"""
    return TimeInstant(
        id=str(uuid.uuid4()),
        iso=datetime.now().isoformat(),
        epoch=datetime.now().timestamp(),
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
        hour=datetime.now().hour,
        minute=datetime.now().minute,
        second=datetime.now().second,
    )


def create_interval(start: TimeInstant, end: TimeInstant) -> TimeInterval:
    """Create time interval"""
    return TimeInterval(
        id=str(uuid.uuid4()),
        start=start,
        end=end,
    )


def create_point(lat: float, lon: float, label: str = "") -> GeoPoint:
    """Create geo point"""
    return GeoPoint(
        id=str(uuid.uuid4()),
        lat=lat,
        lon=lon,
        label=label,
    )


__all__ = [
    'TimePrecision',
    'TimeInstant', 'Duration', 'TimeInterval',
    'GeoPrecision', 'GeoCRS',
    'GeoPoint', 'GeoRegion', 'Place', 'Distance',
    'Spatiotemporal', 'Event', 'Trajectory',
    'TimeSeriesPoint', 'TimeSeries',
    'SpatialRelationship', 'Zone',
    'haversine', 'now', 'create_interval', 'create_point'
]