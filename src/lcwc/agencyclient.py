from lcwc.agency import Agency
from lcwc.category import IncidentCategory


import aiohttp
from bs4 import BeautifulSoup


import logging


class AgencyClient:
    """Client used for fetching lists of agencies from the LCWC website"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def get_agencies(
        self, session: aiohttp.ClientSession, categories: list[IncidentCategory]
    ) -> list[Agency]:
        """Fetches a list of agencies for the given categories"""

        # ids are not zero-indexed unlike almost everywhere else
        id_map = {
            IncidentCategory.FIRE: 1,
            IncidentCategory.MEDICAL: 2,
            IncidentCategory.TRAFFIC: 3,
        }

        agencies = []

        # we need to fetch each category separately because the aggregate page doesn't clarify which category each agency belongs to
        for cat in categories:
            if cat not in id_map:
                self.logger.error(f"Invalid category in agency lookup: {cat}")
            id = id_map[cat]
            url = f"https://www.lcwc911.us/about/agencies-dispatched?field_agency_type_target_id={id}"

            async with session.get(url) as resp:
                parsed_agencies = self.__parse_agencies_page(await resp.text(), cat)
                agencies.extend(parsed_agencies)

        return agencies

    def __parse_agencies_page(
        self, html: str, category: IncidentCategory
    ) -> list[Agency]:
        agencies = []

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "views-table"})

        if table is None:
            self.logger.error("Unable to find agencies table")
            return agencies

        rows = table.find_all("tr")
        if rows is None or len(rows) == 0:
            self.logger.error("Unable to find agencies table rows")
            return agencies

        for index, row in enumerate(rows):
            # skip the first row because it's the header
            if index == 0:
                continue

            id_cell = row.find("td", {"class": "views-field-field-radio-id"})
            title_cell = row.find("td", {"class": "views-field-title"})
            address_cell = row.find("td", {"class": "views-field-field-address"})
            city_cell = row.find("td", {"class": "views-field-field-city"})
            state_cell = row.find("td", {"class": "views-field-field-state"})
            zip_cell = row.find("td", {"class": "views-field-field-zip"})
            phone_cell = row.find("td", {"class": "views-field-field-phone"})

            if (
                id_cell is None
                or title_cell is None
                or address_cell is None
                or city_cell is None
                or state_cell is None
                or zip_cell is None
                or phone_cell is None
            ):
                self.logger.error(
                    f"One or more cells missing from agencies table: {row}"
                )
                continue

            station_number = id_cell.text.strip()
            name = title_cell.text.strip()
            url = title_cell.find("a")["href"]
            address = address_cell.text.strip()
            city = city_cell.text.strip()
            state = state_cell.text.strip()
            zip_code = zip_cell.text.strip()
            phone = phone_cell.text.strip()

            agencies.append(
                Agency(
                    category=category,
                    station_number=station_number,
                    name=name,
                    url=url,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    phone=phone,
                )
            )

        return agencies
