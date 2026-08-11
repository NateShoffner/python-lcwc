from typing import Optional


class UnitConverter:
    """Converts shorthand unit abbreviations into their long-hand names

    The ArcGIS feed condenses unit names into an abbreviation and an id
    (ex: "ENG531"), so the abbreviation has to be expanded separately to render
    a unit the way the web and RSS feeds spell it out.
    """

    def __init__(self):
        self.mapping = {
            # Fire
            "BRU": "Brush",
            "DEP": "Deputy",
            "ENG": "Engine",
            "RES": "Rescue",
            "SQU": "Squad",
            "TAC": "Tactical",
            "TAN": "Tanker",
            "TRA": "Tractor",
            "TRK": "Truck",
            "UTV": "Utility Vehicle",
            # Medical
            "AMB": "Ambulance",
            "MED": "Medic",
            "QRS": "Quick Response Service",
            # Air
            "AIR": "Air",
            # Traffic
            "P": "Police",
        }

    def register(self, short_hand: str, long_hand: str) -> None:
        """Registers a shorthand abbreviation, replacing any existing entry

        :param short_hand: The abbreviation as it appears in a unit name
        :param long_hand: The name the abbreviation expands to
        """
        self.mapping[short_hand.upper()] = long_hand

    def unregister(self, short_hand: str) -> None:
        """Removes a shorthand abbreviation, ignoring unknown ones

        :param short_hand: The abbreviation to remove
        """
        self.mapping.pop(short_hand.upper(), None)

    def convert(self, short_hand: str) -> Optional[str]:
        """Expands the given abbreviation into its long-hand name

        :param short_hand: The abbreviation as it appears in a unit name
        :return: The long-hand name, or None if the abbreviation is unknown
        :rtype: Optional[str]
        """
        return self.mapping.get(short_hand.upper())
