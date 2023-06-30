import datetime
from lcwc.web.incident import Incident
from lcwc.category import IncidentCategory
from collections import namedtuple

Coordinates = namedtuple("Coordinates", ["longitude", "latitude"])


class ArcGISIncident(Incident):
    """Represents an incident from the live ArcGIS REST API"""

    def __init__(
        self,
        category: IncidentCategory,
        date: datetime,
        description: str,
        municipality: str,
        intersection: str,
        number: int,
        priority: int,
        agency: str,
        public: bool,
        coordinates: Coordinates,
        units: list[str] = [],
    ) -> None:
        super().__init__(category, date, description, municipality, intersection, units)
        self._incident_number = number
        self._priority = priority
        self._agency = agency
        self._public = public
        self._coordinates = coordinates

    @property
    def number(self) -> int:
        """Returns the number of the incident"""
        return self._incident_number

    @property
    def priority(self) -> int:
        """Returns the priority of the incident"""
        return self._priority

    @property
    def agency(self) -> str:
        """Returns the agency of the incident"""
        return self._agency

    @property
    def coordinates(self) -> Coordinates:
        """Returns the coordinates of the incident"""
        return self._coordinates

    @property
    def public(self) -> bool:
        """Returns whether the incident is public"""
        return self._public
