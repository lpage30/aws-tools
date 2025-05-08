from datetime import datetime
import json

def to_dict_value(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return o.__dict__

def json_dumps(o):
    return json.dumps(o, default=to_dict_value, sort_keys=True, indent=4)

def json_dump(o, writeableFp):
    return json.dump(o, writeableFp, default=to_dict_value, sort_keys=True, indent=4)


def json_loads(s):
    return json.loads(s)

def json_load(readableFp):
    return json.load(readableFp)