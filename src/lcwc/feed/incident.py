from dataclasses import dataclass
from lcwc.incident import Incident


@dataclass
class FeedIncident(Incident):
    """Represents an incident from the live incident feed"""

    """Returns the guid of the incident"""
    guid: str
