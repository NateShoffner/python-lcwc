import aiohttp
import asyncio
from lcwc import feedclient

async def main():

    client = feedclient.IncidentFeedClient()
    
    async with aiohttp.ClientSession() as session:
        incidents = await client.fetch_and_parse(session)

        for incident in incidents:
            print("-----")
            print(f'Category: {incident.category}')
            print(f'Date: {incident.date}')
            print(f'Description: {incident.description}')
            print(f'Intersection: {incident.intersection}')
            print(f'Township: {incident.township}')
            units = 'None' if len(incident.units) == 0 else ', '.join(incident.units)
            print(f'Units: {units}')

            if isinstance(incident, feedclient.FeedIncident):
                print(f'GUID: {incident.guid}')

        print("-----")     

if __name__ == '__main__':
    asyncio.run(main())