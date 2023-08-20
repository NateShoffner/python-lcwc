from dataclasses import dataclass
from typing import Optional

from lcwc.agencies.agency import Agency


@dataclass(eq=False)
class Unit:
    """Represents a unit responding to an incident"""

    """ The fully-qualified name of the unit """
    full_name: str = None

    """ The fully-qualified name is using shorthand notation """
    is_shorthand: Optional[bool] = False

    """ The name of the unit """
    name: Optional[str] = None

    """ The agency associated with the unit """
    agency: Optional[Agency] = None

    """ The ID of the agency associated with the unit """
    station_id: Optional[str] = None

    """ The unit ID """
    id: Optional[int] = None

    """ The unit originates from outside of the county """
    out_of_county: Optional[bool] = False

    """ The name of the county the unit originates from """
    county_name: Optional[str] = None

    """ The unit is pending assignment """
    pending: Optional[bool] = False

    def __eq__(self, other):
        if not isinstance(other, Unit):
            return NotImplemented
        return self.full_name == other.full_name

    def __str__(self) -> str:
        if self.full_name:
            return self.full_name
        return self.__repr__()
