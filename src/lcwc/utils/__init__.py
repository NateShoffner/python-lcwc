import datetime
from lcwc.category import IncidentCategory
from lcwc.web.incident import WebIncident as Incident

""" A list of keywords that indicate a location name"""
FIRE_UNIT_NAMES = [
    "ATV",
    "BATTALION",
    "BOAT",
    "BRUSH",
    "CHIEF",
    "DEPUTY",
    "DUTY OFFICER",
    "ENGINE",
    "FIRE POLICE",
    "FOAM",
    "RESCUE",
    "SQUAD",
    "TAC",
    "TRUCK",
    "UTILITY",
    "UTV",
]

""" A list of keywords that indicate a location name """
MEDICAL_UNIT_NAMES = ["AMB", "EMS", "INT", "MEDIC", "QRS"]

""" A list of keywords that indicate a location name """
LOCATION_NAMES = [
    "ALY",
    "AVE",
    "CIR",
    "CT",
    "DR",
    "LN",
    "PL",
    "PIKE",
    "RAMP",
    "RD",
    "ROUTE",
    "ST",
]

""" A list of keywords that indicate a medical incident """
MEDICAL_DESCRIPTION_KEYWORDS = ["MEDICAL"]

""" A list of keywords that indicate a fire incident """
FIRE_DESCRIPTION_KEYWORDS = ["FIRE"]

""" A list of keywords that indicate a traffic incident """
TRAFFIC_DESCRIPTION_KEYWORDS = ["TRAFFIC", "VEHICLE"]


def determine_category(description: str, units: list[str]) -> IncidentCategory:
    """Determines the category of an incident based on the description and units assigned

    :param description: The description of the incident
    :param units: The units assigned to the incident
    :return: The category of the incident
    :rtype: IncidentCategory
    """

    # check for unit matches
    for unit in units:
        if any(k in unit for k in FIRE_UNIT_NAMES):
            return IncidentCategory.FIRE
        elif any(k in unit for k in MEDICAL_UNIT_NAMES):
            return IncidentCategory.MEDICAL

    # extra note regarding traffic incidents: they tend to not have units assigned
    # unless there is an accompanying fire or medical incident for the same call
    # this needs to be checked before the description check for other categories
    if len(units) == 0 and any(k in description for k in TRAFFIC_DESCRIPTION_KEYWORDS):
        return IncidentCategory.TRAFFIC

    # perform a basic description check
    if any(k in description for k in MEDICAL_DESCRIPTION_KEYWORDS):
        return IncidentCategory.MEDICAL
    if any(k in description for k in FIRE_DESCRIPTION_KEYWORDS):
        return IncidentCategory.FIRE

    return IncidentCategory.UNKNOWN


def is_related_incident(a: Incident, b: Incident, delta: datetime.timedelta) -> bool:
    """Determines if two incidents are related based on the intersection and time delta

    :param a: The first incident
    :param b: The second incident
    :param delta: The time delta
    :return: True if the incidents are related, False otherwise
    :rtype: bool
    """

    if a.intersection is None or b.intersection is None:
        return False
    return a.intersection == b.intersection and abs(a.date - b.date) <= delta
