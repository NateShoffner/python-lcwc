import aiohttp
from lcwc import Client
from lcwc.agencies.agencyresolver import AgencyResolver
from lcwc.web.incident import WebIncident as Incident
from lcwc.web.parser import WebParser


class WebClient(Client):
    """Client for scraping the live incident page"""

    URL = "https://www.lcwc911.us/live-incident-list"
    """ The URL of the live incident page """

    def __init__(self, agency_resolver: AgencyResolver = AgencyResolver()) -> None:
        self.agency_resolver = agency_resolver
        self.parser = WebParser()

    @property
    def name(self) -> str:
        """Returns the name of the client"""
        return "WebClient"

    async def get_incidents(
        self, session: aiohttp.ClientSession, timeout: int = 10
    ) -> list[Incident]:
        """Fetches the live incident page and returns a list of incidents

        :param session: The aiohttp session to use
        :param timeout: The timeout in seconds
        :return: A list of incidents
        :rtype: list[Incident]
        """
        html = None
        async with session.get(self.URL, timeout=timeout) as resp:
            if resp.status == 200:
                html = await resp.read()
            else:
                raise Exception(f"Unable to fetch live incident page: {resp.status}")

        return self.parser.parse(html, self.agency_resolver)
