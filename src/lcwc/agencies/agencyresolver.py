import re
from lcwc.agencies import ALL_KNOWN_AGENCIES
from lcwc.agencies.agency import Agency
from lcwc.agencies.exceptions import OutOfCountyException, PendingUnitException
from lcwc.category import IncidentCategory
from lcwc.incident import Incident
from lcwc.unit import Unit


class AgencyResolver:
    """Collection of dispatch and various lookup methods"""

    def __init__(self, load_known: bool = True):
        self.agencies = ALL_KNOWN_AGENCIES if load_known else []

    def add_agency(self, agency: Agency):
        self.agencies.append(agency)

    def remove_agency(self, agency: Agency):
        self.agencies.remove(agency)

    def get_agency(self, station_id: str, category: IncidentCategory) -> Agency:
        """Attempts to find the agency associated with the given station id and category within the list of agencies provided"""
        for agency in self.agencies:
            if agency.station_number == station_id and agency.category == category:
                return agency

    def get_agencies(self, category: IncidentCategory) -> list[Agency]:
        return [agency for agency in self.agencies if agency.category == category]

    def get_all_agencies(self) -> list[Agency]:
        return self.agencies

    def get_unit_agency(self, unit: Unit, category: IncidentCategory) -> Agency:
        """Attempts to find the agency associated with the given unit and category within the list of agencies provided"""

        if unit.is_shorthand():
            return self.__unit_short_name_to_agency(unit, category)
        else:
            return self.__unit_name_to_agency(unit, category)
