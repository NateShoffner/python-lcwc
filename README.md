# python-lcwc

python-lcwc is a Python library for the [LCWC](https://www.lcwc911.us/live-incident-list) incident feed.

The library features multiple clients for retrieving incidents: a web scraper, an RSS feed parser, and an ArcGIS REST client. See notes below for more information.

## Installation

    pip install lcwc

## Example

```python
import asyncio
import aiohttp
from lcwc.feed import FeedClient


async def main():
    client = FeedClient()

    async with aiohttp.ClientSession() as session:
        incidents = await client.get_incidents(session)

        for incident in incidents:
            print(f'{incident.date} - {incident.description}')


asyncio.run(main())
```

## Notes

### Web Client

The web client uses web-scraping which can be a bit limited for identification purposes but is the most reliable. The web client is the recommended client for use unless you need more granular information such as static identifers.

### Feed Client

The feed client uses the RSS feed and is similar to the web client except it overs an (admittedly arbitrary) GUID for each incident. Categorization can be a bit off since the feed doesn't supply that in formation so we have to attempt to extrapolate the category from the incident description/units assigned. Use the web client if you need more accurate categorization.

### ArcGIS REST Client

The ArcGIS REST client uses the ArcGIS REST API to retrieve incidents. This is the most accurate client since it uses the same data source as the LCWC website. This is still a bit of a prototype and may be subject to change. The ArcGIS REST client is the recommended client if you need more granular information such as static identifiers and coordinates.

Note that `coordinates` is `None` for incidents the service has not geocoded, and that the service does not publish non-emergency EMS activity (`ROUTINE TRANSFER`, `EMS ACTIVITY`) at all. See [ArcGIS live feed service behavior](docs/arcgis-service-behavior.md) for the measured details.