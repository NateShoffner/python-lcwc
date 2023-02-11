from enum import Enum

class IncidentCategory(str, Enum):
    """ Represents the category of an incident """
    FIRE = 'Fire'
    """ Fire incident """
    MEDICAL = 'Medical'
    """ Medical incident """
    TRAFFIC = 'Traffic'
    """ Traffic incident """
    UNKNOWN = 'Unknown'
    """ Unknown incident """
