import logging
import aiohttp
import datetime
import json
import re

import pytz
from lcwc import Client
from lcwc.arcgis.incident import ArcGISIncident, Coordinates
from lcwc.category import IncidentCategory
from lcwc.unit import Unit
from lcwc.utils.restadapter import RestAdapter, RestException


class ArcGISClient(Client):
    """Client for the ArcGIS REST API"""

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "ArcGISClient"

    async def get_incidents(
        self, session: aiohttp.ClientSession, timeout: int = 10
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

        incidents = []

        for cat in IncidentCategory:
            if cat == IncidentCategory.UNKNOWN:
                continue

            if cat not in layer_mapping:
                self.logger.error(f"No layer mapping for {cat}")
                continue

            layer_id = layer_mapping[cat]

            """ Actual spatial extent of Lancaster County based LanCo GIS data
            lanco_spatial = {
                'xmin': -8548898.732776089,
                'ymin': 4845979.963808246,
                'xmax': -8432714.449782776,
                'ymax': 4909881.3194545675,
                'spatialReference': {
                    'wkid': 102100
                }
            }
            """

            # seems we need to expand the spatial extent to get all incidents
            lanco_spatial = {
                "xmin": -8657540.868810708,
                "ymin": 4794222.228992932,
                "xmax": -8290643.133041878,
                "ymax": 5048910.407239126,
                "spatialReference": {"wkid": 102100},
            }

            params = {
                "f": "json",
                "where": "1=1",
                "returnGeometry": "true",
                "spatialRel": "esriSpatialRelIntersects",
                "geometry": json.dumps(lanco_spatial),
                "geometryType": "esriGeometryEnvelope",
                "inSR": 102100,
                "outFields": ",".join(fields[cat]),
                "outSR": 4326,  # return coordinates in WGS84
                "currentTimestamp": int(
                    datetime.datetime.now().timestamp() * 1000
                ),  # add a timestamp to prevent caching
            }

            adapter = RestAdapter(
                session,
                "utility.arcgis.com",
                "usrsvcs/servers/a1f6aa7faab44b1582029509c46dce86/rest/services/Maps/Public_LiveFeeds/MapServer/",
            )

            try:
                resp = await adapter.get(endpoint=f"{layer_id}/query", ep_params=params)

            except RestException as e:
                self.logger.error(f"{cat} Error: {e}")
                continue

            self.logger.debug(f"{resp.url}")

            if resp.status_code != 200:
                self.logger.error(f"Error: {resp.status_code} for {cat}")
                continue

            error = resp.data.get("error", None)
            if error:
                self.logger.error(f"Response error: {error}")
                continue

            if "features" not in resp.data:
                continue

            for feature in resp.data["features"]:
                incident = self.__parse_incident(cat, feature)
                incidents.append(incident)

        return incidents

    def __parse_incident(
        self, category: IncidentCategory, incident: dict
    ) -> ArcGISIncident:
        attributes = incident["attributes"]
        geometry = incident["geometry"]


        # convert date to UTC

        raw_date = datetime.datetime.fromtimestamp(attributes["IncidentOrigination"] / 1000)
        local_tz = pytz.timezone("America/New_York")
        local_dt = local_tz.localize(raw_date, is_dst=None)  
        date = local_dt.astimezone(pytz.utc)
        
        municipality = attributes["IncidentMunicipality"]

        intersection = re.sub(
            " +", " ", attributes["PublicLocation"]
        )  # collapse multiple spaces

        # unit names are condensed, lacking spaces and delimiters (ex: MED8611)
        if "CurrentUnits" in attributes and attributes["CurrentUnits"] is not None:
            unit_names = attributes["CurrentUnits"].split(",")
            units = [Unit(unit_name) for unit_name in unit_names]
        else:
            units = []

        number = int(attributes["IncidentNumber"])

        if "Priority" in attributes:
            priority = int(attributes["Priority"])
        else:
            priority = None
        agency = attributes["PrimaryAgency"]
        public = bool(attributes["IsPublic"])
        description = attributes["PublicType"]

        coords = Coordinates(geometry["x"], geometry["y"])

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
            coords
        )
        return incident
