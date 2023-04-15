import aiohttp
import datetime
import email.utils 
import feedparser
from lcwc.category import IncidentCategory
from lcwc.client import Client
from lcwc.incident import Incident

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

# custom class to handle the guid attribute
# a bit usless on its own but might be useful for statically identifying incidents
# since apparently every detail is subject to change except maybe the timestamp
class FeedIncident(Incident):
    """ Represents an incident from the live incident feed """

    def __init__(self, category: IncidentCategory, date: datetime, description: str, township: str, intersection: str, units: list[str] = [], guid: str = None) -> None:
        super().__init__(category, date, description, township, intersection, units)
        self._guid = guid

    @property
    def guid(self) -> str:
        """ Returns the guid of the incident """
        return self._guid

class IncidentFeedClient(Client):

    URL = 'https://webcad.lcwc911.us/Pages/Public/LiveIncidentsFeed.aspx'
    """ The URL of the live incident feed """

    FIRE_UNIT_NAMES = ['BRUSH', 'CHIEF', 'DEPUTY', 'DUTY OFFICER', 'ENGINE', 'FIRE POLICE', 'RESCUE', 'SQUAD', 'TRUCK', 'UTV']
    MEDICAL_UNIT_NAMES = ['AMB', 'EMS', 'INT', 'MEDIC', 'QRS']

    LOCATION_NAMES = ['ALY', 'AVE', 'CIR', 'CT', 'DR', 'LN', 'PL', 'PIKE', 'RAMP', 'RD', 'ROUTE', 'ST']

    MEDICAL_DESCRIPTION_KEYWORDS = ['MEDICAL']
    FIRE_DESCRIPTION_KEYWORDS = ['FIRE']
    TRAFFIC_DESCRIPTION_KEYWORDS = ['TRAFFIC']

    def __init__(self):
        super().__init__()

    async def fetch(self, session: aiohttp.ClientSession, timeout: int = 10) -> bytes:
        """ Gets the live incident feed and returns the xml as bytes

        :param session: The aiohttp session to use
        :param timeout: The timeout in seconds
        :return: The xml of the live incident feed
        :rtype: bytes
        """
        async with session:
            html = await super().fetch(session, timeout)
            return html

    def parse(self, contents: bytes) -> list[FeedIncident]:
        """ Parses the live incident feed and returns a list of incidents

        :param contents: The xml of the live incident feed
        :return: A list of incidents
        :rtype: list[Incident]
        """
        incidents = []

        d = feedparser.parse(contents)

        for entry in d.entries:

            # [township];[intersection];[units assigned]
            details_split = entry['description'].strip().split(';', maxsplit=3)

            # first item is always the township
            township = details_split[0].strip()

            intersection = None
            units = []

            def split_units(units_data: str) -> list[str]:
                units_data = units_data.strip()
                if units_data == '':
                    return []
                return [u.strip() for u in units_data.strip().split('<br />')]

            # intersection is not always present, so we need to check for it before splitting the units
            has_unit_names = any(k in details_split[1] for k in self.FIRE_UNIT_NAMES + self.MEDICAL_UNIT_NAMES)
            has_intersection = any(k in details_split[1] for k in self.LOCATION_NAMES)

            if has_unit_names and not has_intersection:
                units = split_units(details_split[1])
            else:
                intersection = details_split[1].strip()
                units = split_units(details_split[2])

            date = datetime.datetime.fromtimestamp( email.utils.mktime_tz(email.utils.parsedate_tz(entry.published)))

            guid = entry.guid

            description = entry.title
            cat = self.__determine_category(description, units)
            incidents.append(FeedIncident(cat, date, description, township, intersection, units, guid))

        return incidents

    async def fetch_and_parse(self, session: aiohttp.ClientSession, timeout: int = 10) -> list[FeedIncident]:
        """ Gets the live incident feed and returns a list of incidents

        :param session: The aiohttp session to use
        :param timeout: The timeout for the request
        :return: A list of incidents
        :rtype: list[Incident]
        """
        result = await self.fetch(session, timeout)
        active_incidents = self.parse(result)
        return active_incidents

    def __determine_category(self, description: str, units: list[str]) -> IncidentCategory:
        """ Determines the category of an incident based on the description and units assigned 
        
        :param description: The description of the incident
        :param units: The units assigned to the incident
        :return: The category of the incident
        :rtype: IncidentCategory
        """

        # check for unit matches 
        for unit in units:
            if any(k in unit for k in self.FIRE_UNIT_NAMES):
                return IncidentCategory.FIRE
            elif any(k in unit for k in self.MEDICAL_UNIT_NAMES):
                return IncidentCategory.MEDICAL

        # perform a basic description check
        if any(k in description for k in self.MEDICAL_DESCRIPTION_KEYWORDS):
            return IncidentCategory.MEDICAL
        if any(k in description for k in self.FIRE_DESCRIPTION_KEYWORDS):
            return IncidentCategory.FIRE

        # extra note regarding traffic incidents: they tend to not have units assigned
        # unless there is an accompanying fire or medical incident for the same call
        if any(k in description for k in self.TRAFFIC_DESCRIPTION_KEYWORDS):
            return IncidentCategory.TRAFFIC

        return IncidentCategory.UNKNOWN