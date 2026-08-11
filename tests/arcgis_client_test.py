import aiohttp
import datetime
import os
import subprocess
import sys
import unittest
from lcwc.arcgis import ArcGISClient, ArcGISIncident
from lcwc.category import IncidentCategory
from unittest import IsolatedAsyncioTestCase


def make_feature(origination_ms: int) -> dict:
    """Builds a minimal ArcGIS feature with the given IncidentOrigination"""
    return {
        "attributes": {
            "IncidentNumber": "2026000123",
            "IncidentMunicipality": "MANHEIM TOWNSHIP",
            "IncidentOrigination": origination_ms,
            "PrimaryAgency": "MANHEIM TWP",
            "CurrentUnits": None,
            "PublicLocation": "MAIN ST  &  BROAD ST",
            "PublicType": "MEDICAL EMERGENCY",
            "IsPublic": True,
        },
        "geometry": {"x": -76.3, "y": 40.0},
    }


def parse_date(origination_ms: int) -> datetime.datetime:
    """Parses a feature and returns the date of the resulting incident"""
    client = ArcGISClient()
    # the parser is private and every public entry point hits the network
    incident = client._ArcGISClient__parse_incident(
        IncidentCategory.MEDICAL, make_feature(origination_ms), None
    )
    return incident.date


def probe(origination_ms: int) -> str:
    """Returns the parsed date alongside the host-local rendering of the same
    epoch, so a caller in another process can tell whether TZ took effect"""
    local = datetime.datetime.fromtimestamp(origination_ms / 1000)
    return f"{parse_date(origination_ms).isoformat()} {local.isoformat()}"


""" IncidentOrigination in epoch milliseconds, and the absolute instant it denotes """
DATE_CASES = [
    # 2026-07-04 14:30 EDT
    (
        1783189800000,
        datetime.datetime(2026, 7, 4, 18, 30, tzinfo=datetime.timezone.utc),
    ),
    # 2026-01-15 09:15 EST
    (
        1768486500000,
        datetime.datetime(2026, 1, 15, 14, 15, tzinfo=datetime.timezone.utc),
    ),
    # 2026-08-09 21:28 EDT, which is the next calendar day in UTC
    (
        1786325280000,
        datetime.datetime(2026, 8, 10, 1, 28, tzinfo=datetime.timezone.utc),
    ),
]

""" Posix-style TZ values the C runtime understands on both Windows and Unix """
TZ_VALUES = ["UTC0", "EST5EDT", "PST8PDT", "JST-9"]

CHILD_PROBE = "import sys; import arcgis_client_test as t; print(t.probe(int(sys.argv[1])))"


class ArcGISDateTest(unittest.TestCase):
    def test_date_is_absolute_utc_instant(self):
        """The epoch is an absolute instant and must parse to it verbatim"""
        for origination_ms, expected in DATE_CASES:
            with self.subTest(origination_ms=origination_ms):
                date = parse_date(origination_ms)

                self.assertIsNotNone(date.tzinfo, "date must be timezone-aware")
                self.assertEqual(
                    date.utcoffset(), datetime.timedelta(0), "date must be UTC"
                )
                self.assertEqual(date, expected)

    def test_date_is_independent_of_host_timezone(self):
        """The same epoch must parse to the same instant on any host, which the
        localize round-trip broke everywhere outside of Eastern time"""

        # TZ cannot be changed within a running process on Windows and
        # time.tzset() is Unix-only, so each timezone gets its own interpreter
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            p for p in [os.path.dirname(os.path.abspath(__file__))] + sys.path if p
        )

        for origination_ms, expected in DATE_CASES:
            with self.subTest(origination_ms=origination_ms):
                parsed = {}
                local = {}

                for tz in TZ_VALUES:
                    result = subprocess.run(
                        [sys.executable, "-c", CHILD_PROBE, str(origination_ms)],
                        env={**env, "TZ": tz},
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        result.returncode, 0, f"TZ={tz} probe failed: {result.stderr}"
                    )

                    parsed[tz], local[tz] = result.stdout.split()

                if len(set(local.values())) == 1:
                    self.skipTest("TZ is not honored by this platform")

                for tz in TZ_VALUES:
                    self.assertEqual(
                        datetime.datetime.fromisoformat(parsed[tz]),
                        expected,
                        f"date is skewed when the host is on TZ={tz}",
                    )


class ArcGISGeometryTest(unittest.TestCase):
    def test_incident_without_geometry_is_parsed(self):
        """The service leaves geometry null on incidents it has not geocoded,
        and those incidents still belong in the results"""
        client = ArcGISClient()
        feature = make_feature(DATE_CASES[0][0])
        del feature["geometry"]

        incident = client._ArcGISClient__parse_incident(
            IncidentCategory.MEDICAL, feature, None
        )

        self.assertIsNone(incident.coordinates)
        self.assertEqual(incident.number, 2026000123)


class WebClientTest(IsolatedAsyncioTestCase):
    async def test_fetch(self):
        async with aiohttp.ClientSession() as session:
            client = ArcGISClient()
            incidents = await client.get_incidents(session)

            self.assertIsNotNone(incidents)
            self.assertIsInstance(incidents, list, "")

            if not incidents:
                self.skipTest("no active incidents to check")

            first_incident = incidents[0]
            self.assertIsNotNone(first_incident)
            self.assertIsInstance(first_incident, ArcGISIncident, "")

            self.assertIsNotNone(first_incident.category)
            self.assertIsNotNone(first_incident.description)
            self.assertIsNotNone(first_incident.date)
            self.assertIsNotNone(first_incident.municipality)
            self.assertIsInstance(first_incident.units, list, "")
            self.assertIsNotNone(first_incident.number)
            # self.assertIsNotNone(first_incident.priority)
            self.assertIsNotNone(first_incident.agency)
            # coordinates are absent for incidents the service has not geocoded

            numbers = [incident.number for incident in incidents]
            self.assertCountEqual(numbers, set(numbers), "incidents must be unique")


if __name__ == "__main__":
    unittest.main()
