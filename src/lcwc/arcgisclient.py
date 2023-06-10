import datetime
import aiohttp
import re
from collections import namedtuple
from lcwc.category import IncidentCategory
from lcwc.client import Client
from lcwc.incident import Incident

Coordinates = namedtuple("Coordinates", ['Longitude', 'Latitude'])

class ArcGISIncident(Incident):
    
    def __init__(self, category: IncidentCategory, date: datetime, description: str, township: str, intersection: str, number: int, priority: int, agency: str, public: bool, coordinates: Coordinates, units: list[str] = []) -> None:
        super().__init__(category, date, description, township, intersection, units)
        self._incident_number = number
        self._priority = priority
        self._agency = agency
        self._public = public
        self._coordinates = coordinates

    @property
    def number(self) -> int:
        """ Returns the number of the incident """
        return self._incident_number

    @property
    def priority(self) -> int:
        """ Returns the priority of the incident """
        return self._priority
    
    @property
    def agency(self) -> str:
        """ Returns the agency of the incident """
        return self._agency
    
    @property
    def coordinates(self) -> Coordinates:
        """ Returns the coordinates of the incident """
        return self._coordinates

    @property
    def public(self) -> bool:
        """ Returns whether the incident is public """
        return self._public
    
class ArcGISClient(Client):

    async def fetch(self, session: aiohttp.ClientSession, timeout: int) -> bytes:   
        """ Gets the contents of the page and returns the contents as bytes """
        async with session.get(self.URL, timeout=timeout) as resp:
            if resp.status == 200:
                c = await resp.read()
                return c

    def parse(self, contents: bytes) -> list[ArcGISIncident]:
        """ Parses the contents of the page and returns a list of incidents """
        pass

    async def fetch_and_parse(self, session: aiohttp.ClientSession, timeout: int = 10) -> list[ArcGISIncident]:
        """ Fetches the page and parses the contents and returns a list of incidents """

        layer_mapping = {
            IncidentCategory.FIRE: 0,
            IncidentCategory.MEDICAL: 1,
            IncidentCategory.TRAFFIC: 2
        }

        # some fields are only present for certain incident types (ex: Priority is only present for medical and traffic)
        fields = {
            IncidentCategory.FIRE: [
                'IncidentNumber',
                'IncidentMunicipality',
                'IncidentOrigination',
                'PrimaryAgency',
                'CurrentUnits',
                'PublicLocation',
                'PublicType',
                'IsPublic'
            ],

            IncidentCategory.MEDICAL: [
                'IncidentNumber',
                'IncidentMunicipality',
                'IncidentOrigination',
                'PrimaryAgency',
                'CurrentUnits',
                'PublicLocation',
                'PublicType',
                'IsPublic',
                'Priority',
            ],

            IncidentCategory.TRAFFIC: [
                'IncidentNumber',
                'IncidentMunicipality',
                'IncidentOrigination',
                'PrimaryAgency',
                'CurrentUnits',
                'PublicLocation',
                'PublicType',
                'IsPublic',
                'Priority',
            ]
        }
        
        incidents = []
        
        for cat in IncidentCategory:

            if cat == IncidentCategory.UNKNOWN:
                continue

            if cat not in layer_mapping:
                print(f'No layer mapping for {cat}')

            layer_id = layer_mapping[cat]

            params = {
                'f': 'json',
                'where': '1=1',
                'returnGeometry': 'true',
                'outFields': ','.join(fields[cat]),
                'outSR': 4326 # return coordinates in WGS84
            }

            url = f'https://utility.arcgis.com/usrsvcs/servers/a1f6aa7faab44b1582029509c46dce86/rest/services/Maps/Public_LiveFeeds/MapServer/{layer_id}/query'

            async with session.get(url, params=params, timeout=timeout) as resp:

                if resp.status != 200:
                    print(f'Error: {resp.status} for {cat}')
                    continue

                data = await resp.json()

                error = data.get('error', None)
                if error:
                    print(resp.url)
                    print(f'Error: {error}')
                    continue

                if 'features' not in data:
                    continue

                for feature in data['features']:
                    incident = self._parse_incident(cat, feature)
                    incidents.append(incident)

        return incidents
    
    def _parse_incident(self, category: IncidentCategory, incident: dict) -> ArcGISIncident:

        attributes = incident['attributes']
        geometry = incident['geometry']

        date = datetime.datetime.fromtimestamp(attributes['IncidentOrigination'] / 1000)
        township = attributes['IncidentMunicipality']

        intersection = re.sub(' +', ' ', attributes['PublicLocation']) # collapse multiple spaces

        # unit names are condensed, lacking spaces and delimiters (ex: MED8611)
        units = attributes['CurrentUnits'].split(',')
        
        number = int(attributes['IncidentNumber'])

        if 'Priority' in attributes:
            priority = int(attributes['Priority'])
        else:
            priority = None
        agency = attributes['PrimaryAgency']
        public = bool(attributes['IsPublic'])
        description = attributes['PublicType']

        coords = Coordinates(geometry['x'], geometry['y'])

        incident = ArcGISIncident(category, date, description , township, intersection, number, priority, agency, public, coords, units)
        return incident