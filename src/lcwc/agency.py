from pydantic import BaseModel
from lcwc.category import IncidentCategory


class Agency(BaseModel):
    """Represents a stationed agency"""

    """ The category of the agency """
    category: IncidentCategory

    """ The station number of the agency """
    station_number: str

    """ The name of the agency """
    name: str

    """ The URL of the agency """
    url: str

    """ The address of the agency """
    address: str

    """ The city of the agency """
    city: str

    """ The state of the agency """
    state: str

    """ The zip code of the agency """
    zip_code: int

    """ The phone number of the agency """
    phone: str

    def __eq__(self, other):
        if not isinstance(other, Agency):
            return False
        return (
            self.category == other.category
            and self.station_number == other.station_number
        )
