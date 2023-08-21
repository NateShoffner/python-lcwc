import re
from lcwc.agencies.agencyresolver import AgencyResolver
from lcwc.category import IncidentCategory
from lcwc.unit import Unit


class UnitParser:
    @staticmethod
    def parse_unit(
        unit_str: str,
        category: IncidentCategory,
        agency_resolver: AgencyResolver = AgencyResolver(),
    ) -> Unit:
        """Parses the given unit string and returns a Unit object

        :param unit_str: The unit string to parse
        :param category: The category for for the unit
        :param agency_resolver: The agency resolver to use for agency lookups (required for shorthand unit names)
        :return: A Unit object
        :rtype: Unit
        """

        is_shorthand = " " not in unit_str
        if is_shorthand:
            return UnitParser.__parse_short_name(unit_str, category, agency_resolver)
        else:
            return UnitParser.__parse_name(unit_str, category, agency_resolver)

    @staticmethod
    def __parse_name(
        unit_str: str, category: IncidentCategory, agency_resolver: AgencyResolver
    ) -> Unit:
        u = Unit(full_name=unit_str)

        if unit_str == "PENDING":
            u.pending = True
            return u

        # Ex: QRS 10
        # Ex: MEDIC 56-4
        # Ex: AMB 89-1 CHESTER
        match = re.match(
            r"^([a-zA-Z ]+) ([0-9]+)(?:-([0-9]+))?(?: ([a-zA-Z ]+))?", unit_str
        )
        if match is None:
            raise ValueError(f"Unable to parse unit name: {unit_str}")

        name, station_id, identifier, county_name = match.groups()
        u.name = name
        u.station_id = station_id
        u.id = int(identifier)

        if county_name:
            u.county_name = county_name
            u.out_of_county = True

        agency = agency_resolver.get_agency(station_id, category)
        if agency:
            u.agency = agency

        return u

    @staticmethod
    def __parse_short_name(
        unit_str: str, category: IncidentCategory, agency_resolver: AgencyResolver
    ):
        """Identifies the agency associated with the given unit short name"""

        """
        # non-regex alternative for short name parsing
        unit_groups = ["".join(x) for _, x in itertools.groupby(unit.name, key=str.isdigit)]
        abbr = unit_groups[0]
        identifer = unit_groups[1]
        county_abbr = unit_groups[2] if len(unit_groups) > 2 else None
        """

        u = Unit(full_name=unit_str, is_shorthand=True)

        if unit_str == "PENDING":
            u.pending = True
            return u

        # Ex: "ENG531" -> "ENG", "531", None
        # Ex: "AMB891CHE" -> "AMB", "891", "CHE"
        match = re.match(r"([a-zA-Z]+)([0-9]+)([a-zA-Z]*)", unit_str)
        if match is None:
            raise ValueError(f"Unable to parse unit name: {unit_str}")

        abbr, identifer, county_abbr = match.groups()

        u.name = abbr
        u.id = identifer

        # identifer is a collapsed string of both the station id + unit id
        # remember to work with id as a string since leading zeros are important

        # iterate through all the characters in the id and build the agency id and suffix
        for i in range(len(identifer)):
            agency_id_builder = identifer[: i + 1]
            agency_suffix = identifer[i + 1 :]
            # agency id is padded with zeros to 2 digits (ex: "07")
            padded_id = str(agency_id_builder.zfill(2))
            a = agency_resolver.get_agency(padded_id, category)
            if a is not None:
                u.station_id = padded_id
                u.agency = a
            if agency_suffix:
                u.id = int(agency_suffix)

        if county_abbr:
            u.county_name = county_abbr
            u.out_of_county = True

        return u
