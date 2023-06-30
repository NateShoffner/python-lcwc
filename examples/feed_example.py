import aiohttp
import asyncio
from lcwc.feed import FeedClient


async def main():
    client = FeedClient()

    async with aiohttp.ClientSession() as session:
        incidents = await client.get_incidents(session)

        for incident in incidents:
            print("-----")
            print(f"Category: {incident.category}")
            print(f"Date: {incident.date}")
            print(f"Description: {incident.description}")
            print(f"Intersection: {incident.intersection}")
            print(f"Municipality: {incident.municipality}")
            unit_names = [unit.name for unit in incident.units]
            print(f"Units: {'None' if len(unit_names) == 0 else ', '.join(unit_names)}")
            print(f"GUID: {incident.guid}")

        print("-----")


if __name__ == "__main__":
    asyncio.run(main())
