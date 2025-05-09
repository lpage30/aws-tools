from dateutil.parser import parse
from datetime import datetime, timezone
from typing import List

def split_flatten_array_arg(array_arg: List[str], delim = ',') -> List[str]:
    result: List[str] = []
    for arg in array_arg:
        result.extend([newarg for newarg in [item.strip() for item in arg.split(delim)] if 0 < len(newarg)])
    return result

def datetime_from_string(value: str) -> datetime:
    return parse(value).replace(tzinfo=timezone.utc)
