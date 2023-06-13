import aiohttp
import unittest
from lcwc.arcgis import Client
from lcwc.incident import Incident
from unittest import IsolatedAsyncioTestCase

class WebClientTest(IsolatedAsyncioTestCase):

    async def test_fetch(self):
        async with aiohttp.ClientSession() as session:
            client = Client()
            incidents = await client.get_incidents(session)

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
            self.assertIsNotNone(first_incident.number)
            #self.assertIsNotNone(first_incident.priority)
            self.assertIsNotNone(first_incident.agency)
            self.assertIsNotNone(first_incident.coordinates)

if __name__ == '__main__':
    unittest.main()