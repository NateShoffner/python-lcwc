import logging
import aiohttp
import datetime
import re
from typing import Optional

from lcwc import Client
from lcwc.agencies.agencyresolver import AgencyResolver
from lcwc.arcgis.incident import ArcGISIncident, Coordinates
from lcwc.category import IncidentCategory
from lcwc.unit import Unit
from lcwc.utils.restadapter import RestAdapter, RestException
from lcwc.utils.unitparser import UnitParser


class ArcGISException(Exception):
    pass


class ArcGISClient(Client):
    """Client for the ArcGIS REST API"""

    def __init__(self, agency_resolver: Optional[AgencyResolver] = None) -> None:
        super().__init__()
        self.agency_resolver = (
            agency_resolver if agency_resolver is not None else AgencyResolver()
        )
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "ArcGISClient"

    async def get_incidents(
        self,
        session: aiohttp.ClientSession,
        timeout: int = 10,
        throw_on_error: bool = False,
    ) -> list[ArcGISIncident]:
        """Fetches the page and parses the contents and returns a list of incidents"""

        layer_mapping = {
            IncidentCategory.FIRE: 0,
            IncidentCategory.MEDICAL: 1,
            IncidentCategory.TRAFFIC: 2,
        }

        # some fields are only present for certain incident types (ex: Priority is only present for medical and traffic)
        fields = {
            IncidentCategory.FIRE: [
                "IncidentNumber",
                "IncidentMunicipality",
                "IncidentOrigination",
                "PrimaryAgency",
                "CurrentUnits",
                "PublicLocation",
                "PublicType",
                "IsPublic",
            ],
            IncidentCategory.MEDICAL: [
                "IncidentNumber",
                "IncidentMunicipality",
                "IncidentOrigination",
                "PrimaryAgency",
                "CurrentUnits",
                "PublicLocation",
                "PublicType",
                "IsPublic",
                "Priority",
            ],
            IncidentCategory.TRAFFIC: [
                "IncidentNumber",
                "IncidentMunicipality",
                "IncidentOrigination",
                "PrimaryAgency",
                "CurrentUnits",
                "PublicLocation",
                "PublicType",
                "IsPublic",
                "Priority",
            ],
        }

        adapter = RestAdapter(
            session,
            "utility.arcgis.com",
            "usrsvcs/servers/a1f6aa7faab44b1582029509c46dce86/rest/services/Maps/Public_LiveFeeds/MapServer/",
        )

        incidents = []

        for cat in IncidentCategory:
            if cat == IncidentCategory.UNKNOWN:
                continue

            if cat not in layer_mapping:
                self.logger.error(f"No layer mapping for {cat}")
                continue

            layer_id = layer_mapping[cat]

            # The service routinely holds rows whose geometry is null, either
            # because the address has not been geocoded yet or never will be.
            # Any query that asks for geometry (and any spatial filter, which
            # implies one) silently drops those rows, so the incidents are
            # fetched geometry-free and the coordinates are looked up with a
            # second query that only the geocoded rows answer.
            attribute_params = {
                "f": "json",
                "where": "1=1",
                "returnGeometry": "false",
                "outFields": ",".join(fields[cat]),
            }

            geometry_params = {
                "f": "json",
                "where": "1=1",
                "returnGeometry": "true",
                "outFields": "IncidentNumber",
                "outSR": 4326,  # return coordinates in WGS84
            }

            try:
                features = await self.__query_layer(
                    adapter, layer_id, cat, attribute_params
                )
            except (RestException, ArcGISException) as e:
                self.logger.error(f"{cat} Error: {e}")
                if throw_on_error:
                    raise e
                continue

            if not features:
                continue

            # a failed lookup only costs the coordinates, so the incidents are
            # still worth returning without them
            try:
                located = await self.__query_layer(
                    adapter, layer_id, cat, geometry_params
                )
            except (RestException, ArcGISException) as e:
                self.logger.error(f"{cat} Coordinates error: {e}")
                if throw_on_error:
                    raise e
                located = []

            coordinates = {}
            for feature in located:
                geometry = feature.get("geometry")
                if geometry is None:
                    continue
                number = feature["attributes"]["IncidentNumber"]
                coordinates[number] = geometry

            # the same incident occasionally occupies more than one row, once
            # geocoded and once not
            seen = set()

            for feature in features:
                number = feature["attributes"]["IncidentNumber"]
                if number in seen:
                    self.logger.debug(f"Skipping duplicate row for incident {number}")
                    continue
                seen.add(number)

                incident = self.__parse_incident(
                    cat,
                    {
                        "attributes": feature["attributes"],
                        "geometry": coordinates.get(number),
                    },
                    self.agency_resolver,
                )
                incidents.append(incident)

        return incidents

    async def __query_layer(
        self,
        adapter: RestAdapter,
        layer_id: int,
        category: IncidentCategory,
        params: dict,
    ) -> list[dict]:
        """Queries a single layer and returns its raw features"""

        params = dict(params)
        # add a timestamp to prevent caching
        params["currentTimestamp"] = int(datetime.datetime.now().timestamp() * 1000)

        resp = await adapter.get(endpoint=f"{layer_id}/query", ep_params=params)

        self.logger.debug(f"{resp.url}")

        if resp.status_code != 200:
            raise ArcGISException(f"Error: {resp.status_code} for {category}")

        error = resp.data.get("error", None)
        if error:
            raise ArcGISException(f"Response error: {error}")

        return resp.data.get("features", [])

    def __parse_incident(
        self,
        category: IncidentCategory,
        incident: dict,
        agency_resolver: AgencyResolver = None,
    ) -> ArcGISIncident:
        attributes = incident["attributes"]
        geometry = incident.get("geometry")

        # IncidentOrigination is epoch milliseconds, which is already an absolute
        # instant, so it converts directly to UTC with no local timezone involved
        date = datetime.datetime.fromtimestamp(
            attributes["IncidentOrigination"] / 1000, tz=datetime.timezone.utc
        )

        municipality = attributes["IncidentMunicipality"]

        intersection = re.sub(
            " +", " ", attributes["PublicLocation"]
        )  # collapse multiple spaces

        unit_names = []
        # unit names are condensed, lacking spaces and delimiters (ex: MED8611)
        if "CurrentUnits" in attributes and attributes["CurrentUnits"] is not None:
            unit_names = attributes["CurrentUnits"].split(",")

        units = []
        for unit_name in unit_names:
            u = UnitParser.parse_unit(unit_name, category, agency_resolver)
            units.append(u)

        number = int(attributes["IncidentNumber"])

        if attributes.get("Priority") is not None:
            priority = int(attributes["Priority"])
        else:
            priority = None
        agency = attributes["PrimaryAgency"]
        public = bool(attributes["IsPublic"])
        description = attributes["PublicType"]

        coords = Coordinates(geometry["x"], geometry["y"]) if geometry else None

        incident = ArcGISIncident(
            category,
            date,
            description,
            municipality,
            intersection,
            units,
            number,
            priority,
            agency,
            public,
            coords,
        )
        return incident
