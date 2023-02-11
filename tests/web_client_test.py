import aiohttp
import unittest
from lcwc import webclient
from lcwc.incident import Incident
from unittest import IsolatedAsyncioTestCase

class WebClientTest(IsolatedAsyncioTestCase):

    async def test_fetch(self):
        async with aiohttp.ClientSession() as session:
            client = webclient.IncidentWebClient()
            result = await client.fetch(session)

            self.assertIsNotNone(result)
            self.assertGreater(len(result), 0)
            self.assertIsInstance(result, bytes, "")
    
    async def test_parse(self):
        async with aiohttp.ClientSession() as session:
            client = webclient.IncidentWebClient()
            result = await client.fetch(session)

            incidents = client.parse(result)

            self.assertIsNotNone(incidents)     
            self.assertIsInstance(incidents, list, "")

            first_incident = incidents[0]
            self.assertIsNotNone(first_incident)
            self.assertIsInstance(first_incident, Incident, "")

            self.assertIsNotNone(first_incident.category)
            self.assertIsNotNone(first_incident.description)
            self.assertIsNotNone(first_incident.date)
            self.assertIsNotNone(first_incident.township)
            self.assertIsInstance(first_incident.units, list, "")

if __name__ == '__main__':
    unittest.main()