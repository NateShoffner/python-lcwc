import aiohttp
import asyncio
from lcwc.arcgis import ArcGISClient


async def main():
    client = ArcGISClient()

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
            print(f"Number: {incident.number}")
            print(f"Priority: {incident.priority}")
            print(f"Agency: {incident.agency}")
            print(
                f"Coordinates: {incident.coordinates.latitude}, {incident.coordinates.longitude}"
            )

        print("-----")


if __name__ == "__main__":
    asyncio.run(main())
