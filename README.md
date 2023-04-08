# python-lcwc

python-lcwc is a Python library for the [LCWC](https://www.lcwc911.us/live-incident-list) incident feed.

Not affiliated or endorsed by LCWC.

The library features both a web scraper and a RSS feed parser. The web scraper client is more reliable due to the RSS feed not categorizing incidents so we have to attempt to extrapolate the category from the incident description/units assigned. Functionally, it should be mostly accurate but edge cases may pop up. Addtionally, the feed parser offers a GUID. This is a unique identifier for each incident. The web client does not offer this.

## Installation

    pip install lcwc

## Example

```python

import aiohttp
from lcwc import feedclient

client = webclient.IncidentFeedClient()

async with aiohttp.ClientSession() as session:
    incidents = await client.fetch_and_parse(session)

    for incident in incidents:
        print(f'Date: {incident.date}')
        print(f'Description: {incident.description}')
```

## TODO

- [ ] Identify potential duplicate incidents reported under multiple categories (e.g. "Fire" and "Traffic" for vehicle fire)
- [ ] Backing store and event emitter