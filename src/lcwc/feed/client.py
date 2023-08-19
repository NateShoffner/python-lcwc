import aiohttp
from lcwc import Client
from lcwc.agencies.agencyresolver import AgencyResolver
from lcwc.agencies.exceptions import OutOfCountyException

from lcwc.feed.incident import FeedIncident
from lcwc.feed.parser import FeedParser


class FeedClient(Client):
    """Client for the incident RSS feed"""

    URL = "https://webcad.lcwc911.us/Pages/Public/LiveIncidentsFeed.aspx"
    """ The URL of the live incident feed """

    def __init__(self, agency_resolver: AgencyResolver = AgencyResolver()) -> None:
        self.agency_resolver = agency_resolver
        self.parser = FeedParser()

    @property
    def name(self) -> str:
        """Returns the name of the client"""
        return "FeedClient"

    async def get_incidents(
        self, session: aiohttp.ClientSession, timeout: int = 10
    ) -> list[FeedIncident]:
        """Gets the live incident feed and returns a list of incidents

        :param session: The aiohttp session to use
        :param timeout: The timeout for the request
        :return: A list of incidents
        :rtype: list[Incident]
        """
        response = None
        async with session.get(self.URL, timeout=timeout) as resp:
            if resp.status == 200:
                response = await resp.read()
            else:
                raise Exception(f"Unable to fetch live incident feed: {resp.status}")

        return self.parser.parse(response, self.agency_resolver)