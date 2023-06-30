import datetime
from lcwc.web.incident import WebIncident as Incident

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
