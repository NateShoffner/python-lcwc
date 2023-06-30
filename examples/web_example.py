import aiohttp
import asyncio
from lcwc.web import WebClient


async def main():
    client = WebClient()

    async with aiohttp.ClientSession() as session:
        incidents = await client.get_incidents(session)

        for incident in incidents:
            print("-----")
            print(f"Category: {incident.category}")
            print(f"Date: {incident.date}")
            print(f"Description: {incident.description}")
            print(f"Intersection: {incident.intersection}")
            print(f"Municipality: {incident.municipality}")
            units = "None" if len(incident.units) == 0 else ", ".join(incident.units)
            print(f"Units: {units}")

        print("-----")


if __name__ == "__main__":
    asyncio.run(main())
