import aiohttp
import asyncio
from lcwc.arcgis import Client

async def main():

    client = Client()
    
    async with aiohttp.ClientSession() as session:
        incidents = await client.get_incidents(session)

        for incident in incidents:
            print("-----")
            print(f'Category: {incident.category}')
            print(f'Date: {incident.date}')
            print(f'Description: {incident.description}')
            print(f'Intersection: {incident.intersection}')
            print(f'Township: {incident.township}')
            units = 'None' if len(incident.units) == 0 else ', '.join(incident.units)
            print(f'Units: {units}')
            print(f'Number: {incident.number}')
            print(f'Priority: {incident.priority}')
            print(f'Agency: {incident.agency}')
            print(f'Coordinates: {incident.coordinates.latitude}, {incident.coordinates.longitude}')

        print("-----")     

if __name__ == '__main__':
    asyncio.run(main())