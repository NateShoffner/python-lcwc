import datetime
import re
from lcwc.agency import Agency
from lcwc.category import IncidentCategory
from lcwc.unit import Unit
from lcwc.web.incident import WebIncident as Incident


def is_related_incident(a: Incident, b: Incident, delta: datetime.timedelta) -> bool:
    """Determines if two incidents are related based on the intersection and time delta

    :param a: The first incident
    :param b: The second incident
    :param delta: The time delta
    :return: True if the incidents are related, False otherwise
    :rtype: bool
    """

    if a.intersection is None or b.intersection is None:
        return False
    return a.intersection == b.intersection and abs(a.date - b.date) <= delta


# TODO move this to a dedicated utils method for agencies


def find_associated_agency(
    unit: Unit, category: IncidentCategory, agencies: list[Agency]
) -> Agency:
    """Attempts to find the agency associated with the given unit and category within the list of agencies provided"""

    if unit.short_name is not None:
        return __unit_short_name_to_agency(unit, category, agencies)

    if unit.name is not None:
        return __unit_name_to_agency(unit, category, agencies)

    return None


def __unit_name_to_agency(
    unit: Unit, category: IncidentCategory, agencies: list[Agency]
):
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
        # TODO handle out-of-county units
        raise ValueError("Out-of-county units not supported")

    for agency in agencies:
        if agency.station_number == station_id and agency.category == category:
            return agency


def __unit_short_name_to_agency(
    unit: Unit, category: IncidentCategory, agencies: list[Agency]
):
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
        # TODO handle out-of-county units
        raise ValueError("Out-of-county units not supported")

    # identifer is a collapsed string of both the station id + unit id
    # remember to work with id as a string since leading zeros are important

    # iterate through all the characters in the id and build the agency id and suffix
    for i in range(len(identifer)):
        agency_id_builder = identifer[: i + 1]
        agency_suffix = identifer[i + 1 :]

        # agency id is padded with zeros to 2 digits (ex: "07")
        padded_id = str(agency_id_builder.zfill(2))
        for agency in agencies:
            if agency.station_number == padded_id and agency.category == category:
                """
                print(
                    f"Match found for {unit.short_name} -> {agency.name} (Station ID: {agency.station_number}) -> (Unit ID: {agency_suffix})"
                )
                """
                return agency

    return None
