import aiohttp
import datetime
import re
from lcwc.arcgis.incident import ArcGISIncident, Coordinates
from lcwc.category import IncidentCategory

class Client:
    """ Client for the ArcGIS REST API """

    async def get_incidents(self, session: aiohttp.ClientSession, timeout: int = 10) -> list[ArcGISIncident]:
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
                    incident = self.__parse_incident(cat, feature)
                    incidents.append(incident)

        return incidents

    def __parse_incident(self, category: IncidentCategory, incident: dict) -> ArcGISIncident:

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