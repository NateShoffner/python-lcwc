from dataclasses import dataclass
import datetime
from lcwc.incident import Incident
from lcwc.category import IncidentCategory

from lcwc.unit import Unit

@dataclass
class Coordinates:
    """Represents the coordinates of an incident"""

    """ The longitude of the incident """
    longitude: float

    """ The latitude of the incident """
    latitude: float

@dataclass
class ArcGISIncident(Incident):
    """Represents an incident from the live ArcGIS REST API"""

    """ The number of the incident """
    number: int

    """ The priority of the incident """
    priority: int

    """ The agency handling the incident """
    agency: str

    """ Whether the incident is public """
    public: bool

    """ The coordinates of the incident """
    coordinates: Coordinates
