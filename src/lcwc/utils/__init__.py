from lcwc.category import IncidentCategory

FIRE_UNIT_NAMES = [
    'ATV', 
    'BATTALION', 
    'BOAT', 
    'BRUSH', 
    'CHIEF', 
    'DEPUTY', 
    'DUTY OFFICER', 
    'ENGINE', 
    'FIRE POLICE', 
    'FOAM', 
    'RESCUE', 
    'SQUAD', 
    'TAC', 
    'TRUCK', 
    'UTILITY', 
    'UTV'
]

MEDICAL_UNIT_NAMES = [
    'AMB', 
    'EMS', 
    'INT', 
    'MEDIC', 
    'QRS'
]

LOCATION_NAMES = [
    'ALY', 
    'AVE', 
    'CIR', 
    'CT', 
    'DR', 
    'LN', 
    'PL', 
    'PIKE', 
    'RAMP', 
    'RD', 
    'ROUTE', 
    'ST'
]

MEDICAL_DESCRIPTION_KEYWORDS = [
    'MEDICAL'
]

FIRE_DESCRIPTION_KEYWORDS = [
    'FIRE'
]

TRAFFIC_DESCRIPTION_KEYWORDS = [
    'TRAFFIC', 
    'VEHICLE'
]

def determine_category(description: str, units: list[str]) -> IncidentCategory:
    """ Determines the category of an incident based on the description and units assigned 
    
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