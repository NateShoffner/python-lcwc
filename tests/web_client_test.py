import aiohttp
import unittest
from lcwc.web import Client, WebIncident as Incident
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
            self.assertIsNotNone(first_incident.municipality)
            self.assertIsInstance(first_incident.units, list, "")


if __name__ == "__main__":
    unittest.main()
