import aiohttp
import datetime
import feedparser
import pytz
from lcwc.feed.incident import FeedIncident
from lcwc.utils import FIRE_UNIT_NAMES, LOCATION_NAMES, MEDICAL_UNIT_NAMES, determine_category

'''
Example entry:

<item>
    <title>MEDICAL EMERGENCY</title>
    <link>http://www.lcwc911.us/lcwc/lcwc/publiccad.asp</link>
    <description>MARTIC TOWNSHIP; BRIDGE VALLEY RD & LAKE ALDRED TER; MEDIC 56-1; </description>
    <pubDate>Wed, 25 Jan 2023 15:22:54 GMT</pubDate>
    <guid isPermaLink="false">792d7e14-34ef-4907-bb50-86c43cd3d570</guid>
</item>
'''

class Client:
    """ Client for the incident RSS feed """

    URL = 'https://webcad.lcwc911.us/Pages/Public/LiveIncidentsFeed.aspx'
    """ The URL of the live incident feed """

    async def get_incidents(self, session: aiohttp.ClientSession, timeout: int = 10) -> list[FeedIncident]:
        """ Gets the live incident feed and returns a list of incidents

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
                raise Exception(f'Unable to fetch live incident feed: {resp.status}')

        active_incidents = self.__parse(response)
        return active_incidents

    def __parse(self, contents: bytes) -> list[FeedIncident]:
        """ Parses the live incident feed and returns a list of incidents

        :param contents: The xml of the live incident feed
        :return: A list of incidents
        :rtype: list[Incident]
        """
        incidents = []

        d = feedparser.parse(contents)

        def has_intersection(details_segment: str) -> bool:
            return any(k in details_segment for k in LOCATION_NAMES)
            
        def has_unit_names(details_segment: str) -> bool:
            return any(k in details_segment for k in FIRE_UNIT_NAMES + MEDICAL_UNIT_NAMES)

        for entry in d.entries:

            guid = entry.guid
            gmt_date = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
            date = gmt_date.replace(tzinfo=datetime.timezone.utc).astimezone(pytz.utc)
            description = entry.title

            # Possible formats:
            # [township];[intersection];[units assigned]
            # [township];[intersection]
            # [township];[units assigned]
            # [township]
            details_split = entry['description'].strip().split(';', maxsplit=3)

            # first item is always the township
            township = details_split[0].strip()

            intersection = None
            units = []

            # skip if only township is present
            if len(details_split) >= 2:
                if has_unit_names(details_split[1]):
                    units = self.__extract_units(details_split[1])
                else:
                    if has_intersection(details_split[1]):
                        intersection = details_split[1].strip()
                    if len(details_split) > 2 and has_unit_names(details_split[2]):
                        units = self.__extract_units(details_split[2])

            category = determine_category(description, units)

            incidents.append(FeedIncident(category, date, description, township, intersection, units, guid))

        return incidents

    def __extract_units(self, units_data: str) -> list[str]:
        """ Extracts the units from the data string

        :param units_data: The data string containing the units
        :return: A list of units
        :rtype: list[str]
        """
        units_data = units_data.strip()
        if units_data == '':
            return []
        return [u.strip() for u in units_data.strip().split('<br />')]