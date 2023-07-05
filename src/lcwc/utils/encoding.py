import datetime
import json
from lcwc.arcgis.incident import Coordinates
from lcwc.incident import Incident
from lcwc.unit import Unit

# TODO use separate encoders/decoders for each client implementation?


class IncidentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Incident):
            return obj.__dict__
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, Unit):
            return obj.__dict__
        if isinstance(obj, Coordinates):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class IncidentDecoder(json.JSONDecoder):
    def decode(self, s):
        obj = json.loads(s)
        if "date" in obj:
            obj["date"] = datetime.datetime.fromisoformat(obj["date"])
        if "units" in obj:
            obj["units"] = [Unit(**unit) for unit in obj["units"]]
        if "coordinates" in obj:
            obj["coordinates"] = Coordinates(**obj["coordinates"])
        return obj
