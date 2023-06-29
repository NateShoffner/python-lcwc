# custom class to handle the guid attribute
# a bit usless on its own but might be useful for statically identifying incidents
# since apparently every detail is subject to change except maybe the timestamp
import datetime
from lcwc.category import IncidentCategory
from lcwc.incident import Incident


class FeedIncident(Incident):
    """Represents an incident from the live incident feed"""

    def __init__(
        self,
        category: IncidentCategory,
        date: datetime,
        description: str,
        municipality: str,
        intersection: str,
        units: list[str] = [],
        guid: str = None,
    ) -> None:
        super().__init__(category, date, description, municipality, intersection, units)
        self._guid = guid

    @property
    def guid(self) -> str:
        """Returns the guid of the incident"""
        return self._guid
