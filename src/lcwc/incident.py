from abc import ABC
import datetime

from lcwc.category import IncidentCategory
from lcwc.unit import Unit


class Incident(ABC):
    """Represents an incident"""

    def __init__(
        self,
        category: IncidentCategory,
        date: datetime,
        description: str,
        municipality: str,
        intersection: str,
        units: list[Unit] = [],
    ) -> None:
        self._category = category
        self._date = date
        self._description = description
        self._municipality = municipality
        self._intersection = intersection
        self._units = units

    @property
    def category(self) -> IncidentCategory:
        """Returns the category of the incident"""
        return self._category

    @property
    def date(self) -> datetime:
        """Returns the date and time of the incident"""
        return self._date

    @property
    def description(self) -> str:
        """Returns the incident description"""
        return self._description

    @property
    def municipality(self) -> str:
        """Returns the municipality of the incident location"""
        return self._municipality

    @property
    def intersection(self) -> str:
        """Returns the intersection of the incident location"""
        return self._intersection

    @property
    def units(self) -> list[Unit]:
        """Returns a list of units responding to the incident"""
        return self._units
