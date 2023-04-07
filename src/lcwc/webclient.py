import datetime
import aiohttp
from bs4 import BeautifulSoup
from lcwc.category import IncidentCategory
from lcwc.incident import Incident
from lcwc.client import Client

TIMEZONE = 'US/Eastern'
""" The timezone used on the LCWC website """

DATE_FORMAT = '%a, %b %d, %Y %H:%M'
""" The date format used on the LCWC website """

class IncidentWebClient(Client):
    """ Parses the live incident page from the LCWC website """

    URL = 'https://www.lcwc911.us/live-incident-list'
    """ The URL of the live incident page """

    def __init__(self):
        super().__init__()

    async def fetch(self, session: aiohttp.ClientSession, timeout: int = 10) -> bytes:
        """ Gets the live incident page and returns the html as bytes

        :return: The html of the live incident page
        :rtype: bytes
        """
        async with session:
            html = await super().fetch(session, timeout)
            return html

    def parse(self, page_html: bytes) -> list[Incident]:
        """
        Parses the live incident page and returns a list of incidents

        :param page_html: The html of the live incident page
        :return: A list of incidents
        :rtype: list[Incident]
        """

        incidents = []
        
        soup = BeautifulSoup(page_html, 'html.parser')
        containers = soup.find_all('div', class_='live-incident-container')

        for container in containers:
            header = container.find('h2').text
            category = IncidentCategory[header.split()[1].upper()]

            table = container.find('table', class_='live-incidents')

            rows = table.find_all('tr')

            for row in rows:

                date_row = row.find('td', class_='date-row')
                incident_row = row.find('td', class_='incident-row')
                location_row = row.find('td', class_='location-row')
                units_row = row.find('td', class_='units-row')

                if not date_row or not incident_row or not location_row or not units_row:
                    continue

                date = datetime.datetime.strptime(date_row.text.strip(), DATE_FORMAT)
                description = incident_row.text.strip().strip()

                # split location by street(s) and township (if applicable)
                location = [l.strip() for l in location_row.text.strip().split('\n')]

                if len(location) == 1:
                    intersection = None
                    township = location[0]
                else:
                    intersection = location[0]
                    township = location[1]

                # we have to decode manually because of internal <br/> tags
                units = [u.strip() for u in units_row.decode_contents().strip().split('<br/>')]
    
                incident = Incident(category, date, description, township, intersection, units)
                incidents.append(incident)

        return incidents

    async def fetch_and_parse(self, session: aiohttp.ClientSession, timeout: int = 10) -> list[Incident]:
        result = await self.fetch(session)
        active_incidents = self.parse(result)
        return active_incidents