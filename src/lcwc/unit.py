from dataclasses import dataclass
from typing import Optional

from lcwc.agencies.agency import Agency


@dataclass(eq=False)
class Unit:
    """Represents a unit responding to an incident"""

    """ The name of the unit """
    name: Optional[str] = None

    """ The shorthand name of the unit """
    short_name: Optional[str] = None

    # TODO use the actual non-suffixed name as the name and store unit ID separately

    """ The unit originates from outside of the county """
    out_of_county: Optional[bool] = False

    """ The agency associated with the unit """
    agency: Optional[Agency] = None

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return NotImplemented

        if self.short_name:
            return self.short_name == other.short_name
        if self.name:
            return self.name == other.name

    def __str__(self) -> str:
        if self.short_name:
            return self.short_name
        if self.name:
            return self.name
        return self.__repr__()
