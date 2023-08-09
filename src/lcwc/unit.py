from dataclasses import dataclass
from typing import Optional


@dataclass(eq=False)
class Unit:

    """Represents a unit responding to an incident"""

    """ The name of the unit """
    name: Optional[str]

    """ The shorthand name of the unit """
    short_name: Optional[str]

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
