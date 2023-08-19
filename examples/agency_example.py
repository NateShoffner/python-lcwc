import aiohttp
import asyncio
from lcwc.agencies.agencyclient import AgencyClient
from lcwc.category import IncidentCategory


async def main():
    client = AgencyClient()

    async with aiohttp.ClientSession() as session:
        fire_agencies = await client.get_agencies(session, [IncidentCategory.FIRE])

        for agency in fire_agencies:
            print("-----")
            print(f"Name: {agency.name}")
            print(f"Station Number: {agency.station_number}")
            print(f"URL: {agency.url}")
            print(f"Address: {agency.address}")
            print(f"City: {agency.city}")
            print(f"Zip: {agency.zip_code}")
            print(f"Phone: {agency.phone}")


if __name__ == "__main__":
    asyncio.run(main())
