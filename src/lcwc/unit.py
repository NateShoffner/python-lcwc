from dataclasses import dataclass


@dataclass(eq=False)
class Unit:

    """Represents a unit responding to an incident"""

    """ The name of the unit """
    name: str

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return NotImplemented
        return self.name == other.name
