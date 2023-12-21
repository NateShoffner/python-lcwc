import datetime
import logging
from bs4 import BeautifulSoup
import pytz
from lcwc.agencies.agencyresolver import AgencyResolver
from lcwc.agencies.exceptions import OutOfCountyException, PendingUnitException
from lcwc.category import IncidentCategory
from lcwc.utils.unitparser import UnitParser, UnitParserException

from lcwc.web.incident import WebIncident


class WebParser:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def parse(self, html: str, agency_resolver: AgencyResolver) -> list[WebIncident]:
        """Parses the live incident page and returns a list of incidents"""

        incidents = []

        soup = BeautifulSoup(html, "html.parser")
        containers = soup.find_all("div", class_="live-incident-container")

        for container in containers:
            header = container.find("h2").text
            category = IncidentCategory[header.split()[1].upper()]

            table = container.find("table", class_="live-incidents")

            rows = table.find_all("tr")

            for row in rows:
                date_row = row.find("td", class_="date-row")
                incident_row = row.find("td", class_="incident-row")
                location_row = row.find("td", class_="location-row")
                units_row = row.find("td", class_="units-row")

                if (
                    not date_row
                    or not incident_row
                    or not location_row
                    or not units_row
                ):
                    continue

                # convert date to UTC
                local_tz = pytz.timezone("America/New_York")
                raw_date = datetime.datetime.strptime(
                    date_row.text.strip(), "%a, %b %d, %Y %H:%M"
                )
                local_dt = local_tz.localize(raw_date, is_dst=None)
                date = local_dt.astimezone(pytz.utc)

                description = incident_row.text.strip().strip()

                # split location by street(s) and municipality (if applicable)
                location = [l.strip() for l in location_row.text.strip().split("\n")]

                if len(location) == 1:
                    intersection = None
                    municipality = location[0]
                else:
                    intersection = location[0]
                    municipality = location[1]

                # we have to decode manually because of internal <br/> tags
                unit_names = [
                    u.strip()
                    for u in units_row.decode_contents().strip().split("<br/>")
                ]

                units = []
                for unit_name in unit_names:
                    if unit_name == "":
                        continue

                    try:
                        u = UnitParser.parse_unit(unit_name, category, agency_resolver)
                        units.append(u)
                    except OutOfCountyException:
                        self.logger.debug(f"Unit {unit_name} is out of county")
                    except PendingUnitException:
                        self.logger.debug(f"Unit {unit_name} is pending")
                    except UnitParserException:
                        self.logger.debug(f"Unable to parse unit {unit_name}")

                incident = WebIncident(
                    category, date, description, municipality, intersection, units
                )
                incidents.append(incident)

        return incidents
