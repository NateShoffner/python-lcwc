import aiohttp
import asyncio
from lcwc import feedclient, webclient
from lcwc.client import Client

async def get_incidents(client: Client):
    async with aiohttp.ClientSession() as session:
        result = await client.fetch(session)
        incidents = client.parse(result)

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

async def main():
    
    #print('Web Client:')
    #await get_incidents(webclient.IncidentWebClient())
    
    print("Feed Client:")
    await get_incidents(feedclient.IncidentFeedClient())

if __name__ == '__main__':
    asyncio.run(main())