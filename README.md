# python-lcwc

python-lcwc is a Python library for the [LCWC](https://www.lcwc911.us/live-incident-list) incident feed.

Not affiliated or endorsed by LCWC.

The library features both a web scraper and a RSS feed parser. The web scraper client is more reliable due to the RSS not categorizing incidents so we have to attempt to extrapolate the category from the incident description/units assigned. It should be 99% accurate but there may be some inaccuracies. When in doubt, use the web client.

## Example

```python

import aiohttp
from lcwc import webclient

client = webclient.IncidentWebClient()

async with aiohttp.ClientSession() as session:
    result = await client.fetch(session)
    incidents = client.parse(result)

    for incident in incidents:
        print(f'Date: {incident.date}')
        print(f'Description: {incident.description}')
```

## TODO

- [ ] Identify potential duplicate incidents reported under multiple categories (e.g. "Fire" and "Traffic" for vehicle fire)
- [ ] Backing store and event emitter