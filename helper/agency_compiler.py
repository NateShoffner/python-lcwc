"""
    Downloads all agencies from the LCWC API and compiles them into a python file.
"""

import asyncio
import aiohttp
import sys
from lcwc.agencies.agencyclient import AgencyClient
from lcwc.category import IncidentCategory


async def main():
    if len(sys.argv) == 1:
        print("Usage: python agency_compiler.py <output_filename>")
        return

    output_filename = sys.argv[1]

    client = AgencyClient()

    async with aiohttp.ClientSession() as session:
        agencies = await client.get_agencies(
            session,
            [
                IncidentCategory.FIRE,
                IncidentCategory.MEDICAL,
                IncidentCategory.TRAFFIC,
            ],
        )

    print(f"Found {len(agencies)} agencies")

    print(f"Saving to {output_filename}")

    ags = {
        IncidentCategory.FIRE.value.upper(): [
            a for a in agencies if a.category == IncidentCategory.FIRE.value
        ],
        IncidentCategory.MEDICAL.value.upper(): [
            a for a in agencies if a.category == IncidentCategory.MEDICAL.value
        ],
        IncidentCategory.TRAFFIC.value.upper(): [
            a for a in agencies if a.category == IncidentCategory.TRAFFIC.value
        ],
    }

    with open(output_filename, "w") as f:
        for category, agencies in ags.items():
            f.write(f"KNOWN_{category}_AGENCIES = [\n")

            for agency in agencies:
                f.write("    Agency(\n")
                f.write(
                    f"        category=IncidentCategory.{agency.category.value.upper()},\n"
                )
                f.write(f'        station_number="{agency.station_number}",\n')
                f.write(f'        name="{agency.name}",\n')
                f.write(f'        url="{agency.url}",\n')
                f.write(f'        address="{agency.address}",\n')
                f.write(f'        city="{agency.city}",\n')
                f.write(f'        state="{agency.state}",\n')
                f.write(f"        zip_code={agency.zip_code},\n")
                f.write(f'        phone="{agency.phone}"\n')
                f.write("    )")
                if agency != agencies[-1]:
                    f.write(",\n")
            f.write("]\n\n")

        f.write(
            "ALL_KNOWN_AGENCIES = KNOWN_FIRE_AGENCIES + KNOWN_MEDICAL_AGENCIES + KNOWN_TRAFFIC_AGENCIES"
        )


if __name__ == "__main__":
    asyncio.run(main())
