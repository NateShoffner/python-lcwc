import datetime
from lcwc.category import IncidentCategory


class WebIncident:
    """Represents an incident"""

    def __init__(
        self,
        category: IncidentCategory,
        date: datetime,
        description: str,
        municipality: str,
        intersection: str,
        units: list[str] = [],
    ) -> None:
        """Constructor.

        :param IncidentCategory category: The category of the incident

        :param datetime date: The date and time of the incident in local time (EST)

        :param str description: The description of the incident

        :param str municipality: The location of the incident location

        :param str intersection: The intersection of the incident location

        :param list[str] units: A list of units responding to the incident
        """

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
    def location(self) -> str:
        """Returns the full location of the incident"""
        if self._intersection is None:
            return self._municipality
        else:
            return "\n".join([self._intersection, self._municipality])

    @property
    def units(self) -> list[str]:
        """Returns a list of units responding to the incident"""
        return self._units

    @property
    def units_pending(self) -> bool:
        """Returns true if the incident has units pending"""
        return any([unit == "PENDING" for unit in self._units])
