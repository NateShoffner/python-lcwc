from dataclasses import dataclass


@dataclass
class Unit:

    """Represents a unit responding to an incident"""

    """ The name of the unit """
    name: str
