import re
from lcwc.agencies import ALL_KNOWN_AGENCIES
from lcwc.agencies.agency import Agency
from lcwc.agencies.exceptions import OutOfCountyException
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
        for agency in self.agencies:
            if agency.station_number == station_id and agency.category == category:
                return agency

    def get_agencies(self, category: IncidentCategory) -> list[Agency]:
        return [agency for agency in self.agencies if agency.category == category]

    def get_all_agencies(self) -> list[Agency]:
        return self.agencies

    def get_unit_agency(self, unit: Unit, category: IncidentCategory) -> Agency:
        """Attempts to find the agency associated with the given unit and category within the list of agencies provided"""
        if unit.short_name is not None:
            return self.__unit_short_name_to_agency(unit, category)
        if unit.name is not None:
            return self.__unit_name_to_agency(unit, category)

    def __unit_name_to_agency(self, unit: Unit, category: IncidentCategory):
        """Identifies the agency associated with the given unit name"""

        # Ex: QRS 10
        # Ex: MEDIC 56-4
        # Ex: AMB 89-1 CHESTER
        match = re.match(
            r"^([a-zA-Z ]+) ([0-9]+)(?:-([0-9]+))?(?: ([a-zA-Z ]+))?", unit.name
        )
        if match is None:
            raise ValueError(f"Unable to parse unit name: {unit.name}")

        name, station_id, identifier, county_name = match.groups()

        if county_name:
            raise OutOfCountyException("Out-of-county units not supported")

        return self.get_agency(station_id, category)

    def __unit_short_name_to_agency(self, unit: Unit, category: IncidentCategory):
        """Identifies the agency associated with the given unit short name"""

        """
            # non-regex alternative for short_name parsing
            unit_groups = ["".join(x) for _, x in itertools.groupby(unit.short_name, key=str.isdigit)]
            abbr = unit_groups[0]
            identifer = unit_groups[1]
            county_abbr = unit_groups[2] if len(unit_groups) > 2 else None
            """

        # Ex: "ENG531" -> "ENG", "531", None
        # Ex: "AMB891CHE" -> "AMB", "891", "CHE"
        match = re.match(r"([a-zA-Z]+)([0-9]+)([a-zA-Z]*)", unit.short_name)
        if match is None:
            raise ValueError(f"Unable to parse unit name: {unit.short_name}")

        abbr, identifer, county_abbr = match.groups()
        if county_abbr:
            raise OutOfCountyException("Out-of-county units not supported")

        # identifer is a collapsed string of both the station id + unit id
        # remember to work with id as a string since leading zeros are important

        # iterate through all the characters in the id and build the agency id and suffix
        for i in range(len(identifer)):
            agency_id_builder = identifer[: i + 1]
            agency_suffix = identifer[i + 1 :]
            # agency id is padded with zeros to 2 digits (ex: "07")
            padded_id = str(agency_id_builder.zfill(2))
            return self.get_agency(padded_id, category)
