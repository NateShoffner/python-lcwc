from dataclasses import dataclass, field
import datetime

from lcwc.category import IncidentCategory
from lcwc.unit import Unit


@dataclass
class Incident:
    """Represents an incident"""

    """ The category of the incident """
    category: IncidentCategory

    """ The date and time of the incident """
    date: datetime

    """ The description of the incident """
    description: str

    """ The location of the incident location """
    municipality: str

    """ The intersection of the incident location """
    intersection: str

    """ A list of units responding to the incident """
    units: list[Unit]
